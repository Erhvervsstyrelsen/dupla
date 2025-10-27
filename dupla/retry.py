import requests


def stop_retry_on_err(exc: Exception) -> bool:
    """Return True if the http-get action should be cancelled (not retried) due to the received exception.

    Args:
        exc: Exception raised during the HTTP call.

    Returns:
        False for transient failures (network errors, HTTP 5xx, 429),
        Otherwise True.
    """
    # Network-layer problems → retry
    if isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
        return False

    # HTTP errors → inspect status code
    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        status = exc.response.status_code
        if status >= 500 and status < 600:
            return False                    # 5xx server errors
        if status in (429,503):  # too many requests + temporary unable to handle request
            return False
        return True

    # Everything else → don't retry
    return True


