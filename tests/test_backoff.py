from dataclasses import dataclass
import pytest
import requests
import backoff

from dupla.retry import is_retryable

@dataclass
class test_case:
    err_code: int
    expect_retry: bool

@pytest.mark.parametrize("params", [
                             test_case(400, False),
                             test_case(402, False),
                             test_case(408, False),
                             test_case(429, True),
                             test_case(500, True),
                             test_case(600, False),
                          ])
def test_backoff_http_err_handling(params: test_case):
    count = 0

    @backoff.on_exception(
        backoff.constant,
        (requests.exceptions.RequestException),
        giveup=lambda e: not is_retryable(e),
        max_tries=2,
        interval=0.01,
        jitter=None,
    )
    def simulate_get():
        nonlocal count
        count = count + 1
        raise requests.exceptions.HTTPError(response=create_response(params.err_code))
    
    with pytest.raises(Exception):
        simulate_get()
    if params.expect_retry:
        assert count == 2
    else:
        assert count == 1


@pytest.mark.parametrize("status", [429, 503])
def test_backoff_retry_after_header_value(status:int):
    count = 0
    max_retries = 3

    @backoff.on_predicate(
    backoff.runtime,
    predicate=lambda r: r.status_code in (429, 503),
    value=lambda r: float(r.headers.get("Retry-After")),
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
def create_response(status_code: int, retry_after: float | None):
    result = requests.Response()
    result.status_code = status_code
    if retry_after is not None:
        result.headers["Retry-After"] = str(retry_after)
    return result