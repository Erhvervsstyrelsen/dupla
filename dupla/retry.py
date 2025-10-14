import requests

def _is_retryable(exc: Exception) -> bool:
    """
    Decide whether an exception is retryable.

    Args:
        exc (Exception): Exception raised by the HTTP call.

    Returns:
        bool: True if we should retry (5xx or network issues), False for 4xx.
    """
    # Network-layer problems: retry
    if isinstance(exc, (requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout)):
        return True

    # HTTP errors: retry only for 5xx
    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        return 500 <= exc.response.status_code < 600

    # Everything else: don't retry
    return False