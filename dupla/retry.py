import requests


def stop_retry_on_err(exc: Exception) -> bool:
    """Return True if the exception should not be retried.

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
        if status in (429,503):
            return False                    # too many requests
        return True                         # most other 4xx (e.g., 400, 401, 403, 404, 422, 423)

    # Everything else → don't retry
    return True


