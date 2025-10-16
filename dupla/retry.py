import requests

def is_retryable(exc: Exception) -> bool:
    """Return True if the exception should be retried.

    Args:
        exc: Exception raised during the HTTP call.

    Returns:
        True for transient failures (network errors, HTTP 5xx, 429),
        Otherwise False.
    """
    # Network-layer problems → retry
    if isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
        return True

    # HTTP errors → inspect status code
    if isinstance(exc, requests.exceptions.HTTPError) and exc.response is not None:
        status = exc.response.status_code
        if status >= 500 and status < 600:
            return True                    # 5xx server errors
        if status in (429,):
            return True                    # too many requests
        return False                       # most other 4xx (e.g., 400, 401, 403, 404, 422, 423)

    # Everything else → don't retry
    return False
