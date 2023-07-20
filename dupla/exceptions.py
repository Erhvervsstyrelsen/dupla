from typing import Any

__all__ = ["DuplaApiException", "DuplaApiAuthenticationException", "InvalidPayloadException"]


class DuplaApiException(Exception):
    """A general error for the DUPLA API."""


class DuplaResponseException(DuplaApiException):
    """The Dupla response failed"""

    def __init__(self, *args, response: Any = None) -> None:
        self.response = response
        super().__init__(*args)


class DuplaApiAuthenticationException(Exception):
    """The authentication to the DUPLA API errored."""


class InvalidPayloadException(Exception):
    """Current payload is invalid for the payload schema."""
