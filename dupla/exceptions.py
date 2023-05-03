__all__ = ["DuplaApiException", "DuplaApiAuthenticationException", "InvalidPayloadException"]


class DuplaApiException(Exception):
    """A general error for the DUPLA API."""


class DuplaApiAuthenticationException(Exception):
    """The authentication to the DUPLA API errored."""


class InvalidPayloadException(Exception):
    """Current payload is invalid for the payload schema."""
