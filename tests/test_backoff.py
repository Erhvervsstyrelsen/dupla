from dataclasses import dataclass
import pytest
import requests
import backoff

from dupla.retry import stop_retry_on_err


@dataclass
class test_case:
    err_code: int
    expect_retry: bool


@pytest.mark.parametrize(
    "params",
    [
        test_case(400, False),
        test_case(402, False),
        test_case(408, False),
        test_case(429, True),
        test_case(500, True),
        test_case(600, False),
    ],
)
def test_backoff_http_err_handling(params: test_case):
    count = 0

    @backoff.on_exception(
        backoff.constant,
        (requests.exceptions.RequestException),
        giveup=lambda e: stop_retry_on_err(e),
        max_tries=2,
        interval=0.01,
        jitter=None,
    )
    def simulate_get():
        nonlocal count
        count = count + 1
        raise requests.exceptions.HTTPError(response=create_response(params.err_code, None))

    with pytest.raises(Exception):
        simulate_get()
    if params.expect_retry:
        expected = 2
    else:
        expected = 1

    assert count == expected


@pytest.mark.parametrize("status", [429, 503])
def test_backoff_retry_after_header_value(status: int):
    count = 0
    max_retries = 3

    @backoff.on_predicate(
        backoff.runtime,
        predicate=lambda r: r.status_code in (429, 503),
        value=lambda r: float(r.headers.get("Retry-After"), 0.1),
        max_tries=max_retries,
        jitter=None,
    )
    def simulate_get() -> requests.Response:
        nonlocal count
        count = count + 1
        if count < max_retries:
            result = create_response(status, retry_after=0.0)
            assert result.status_code == status
            return result
        return create_response(status_code=200, retry_after=None)

    response = simulate_get()
    assert count == max_retries
    assert response.status_code == 200


@pytest.mark.parametrize(
    "exec_type", [requests.exceptions.ConnectionError, requests.exceptions.Timeout, None]
)
def test_backoff_retry_network_request_error(exec_type: requests.exceptions.RequestException):
    count = 0
    max_tries = 3

    @backoff.on_exception(
        backoff.constant,
        (requests.exceptions.RequestException),
        giveup=lambda e: stop_retry_on_err(e),
        max_tries=max_tries,
        interval=0.01,
        jitter=None,
    )
    def simulate_get():
        nonlocal count
        count = count + 1
        raise exec_type

    with pytest.raises(Exception):
        simulate_get()

    if exec_type:
        assert count == max_tries


def test_stack_exception_outer_predicate_inner_interaction():
    """Exercise on_exception (network) + on_predicate (429/503) together.

    Flow: first attempt raises ConnectionError (handled by on_exception),
    then two 429s with Retry-After=0 (handled by on_predicate), then 200.
    """
    count = 0
    script: list[tuple[str, int]] = [
        ("exc", 0),  # ConnectionError
        ("resp", 429),  # predicate retry
        ("resp", 429),  # predicate retry
        ("resp", 200),  # success
    ]

    @backoff.on_exception(
        backoff.constant,
        (requests.exceptions.ConnectionError, requests.exceptions.Timeout),
        max_tries=2,
        interval=0.01,
        jitter=None,
        giveup=lambda e: False,
    )
    @backoff.on_predicate(
        backoff.runtime,
        predicate=lambda r: r.status_code in (429, 503),
        value=lambda r: float(r.headers.get("Retry-After", 0)),
        max_tries=3,
        jitter=None,
    )
    def simulated_call():
        nonlocal count
        count += 1
        kind, val = script.pop(0)
        if kind == "exc":
            raise requests.exceptions.ConnectionError()
        if kind == "resp" and val in (429, 503):
            return create_response(val, retry_after=0.0)
        if kind == "resp" and val == 200:
            return create_response(200, None)
        raise AssertionError("invalid script state")

    resp = simulated_call()
    assert count == 4
    assert resp.status_code == 200


def create_response(status_code: int, retry_after: float | None):
    result = requests.Response()
    result.status_code = status_code
    if retry_after is not None:
        result.headers["Retry-After"] = str(retry_after)
    return result
