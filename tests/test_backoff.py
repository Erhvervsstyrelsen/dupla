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


def create_response(status_code: int):
    result = requests.Response()
    result.status_code = status_code
    return result