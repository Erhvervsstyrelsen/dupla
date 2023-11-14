import logging
from typing import Any, Dict, List, Optional

import backoff
import requests

from .base import DuplaApiBase
from .exceptions import DuplaApiException, DuplaResponseException
from .payload import BasePayload

logger = logging.getLogger(__file__)

__all__ = ["DuplaAccess"]

RESPONSE_T = Dict[str, Any]


class DuplaAccess(DuplaApiBase):
    """
    Class for accessing the Dataudveklspingsplatformen API (Dupla).
    """

    def __init__(
        self,
        transaction_id: str,
        agreement_id: str,
        pkcs12_filename: str,
        pkcs12_password: str,
        billetautomat_url: str,
        base_url: str = r"https://api.skat.dk",
        jwt_token_expiration_overlap: int = 5,
        max_tries: int = 8,
    ):
        """Instantiates new DUPLA API endpoint client.
        Args:
            base_url (str): The HTTP(S) endpoint of the API.
            transaction_id (str): An ID used to correlate requests across the API.
                Should be constant for IKP-DA.
            agreement_id (str): An ID/token supplied by the API provider.
            pkcs12_filename (str): Path to PKCS12 certificate file.
            pkcs12_password (str): Password for PKCS12 certificate file.
            billetautomat_url (str): Endpoint to the authentication service for requesting
                JWT tokens.
            jwt_token_expiration_overlap (int): The overlap time for token expiration time
                (in seconds) to avoid situations where token is almost expired during the check
                and will be rejected in a next request. Defaults to 5 seconds.
            max_tries (int): Maximum number of times a failed request is re-attempted in
                ``get_data``. Defaults to 8.
        """

        self.base_url = base_url
        self.max_tries = max_tries
        super().__init__(
            transaction_id,
            agreement_id,
            pkcs12_filename,
            pkcs12_password,
            billetautomat_url,
            jwt_token_expiration_overlap,
        )

    def get_endpoint(self, payload: BasePayload) -> str:
        """Retrieve the endpoint URL."""
        return payload.endpoint_from_base_url(self.base_url)

    def get_data(
        self,
        payload: BasePayload,
        endpoint: Optional[str] = None,
    ) -> List[RESPONSE_T]:
        """Request the server for data.

        Args:
            payload (BasePayload): The Pydantic payload model.
            endpoint (Optional[str], optional): An optional endpoint URL override.
                If not provided, it defaults to the url join of the base URL and
                the payload default URL. Defaults to None.
        Returns:
            List[Dict[str, Any]]: A JSON list representing data as returned by the API.
        """
        if endpoint is None:
            endpoint = self.get_endpoint(payload)
        payload_serialized = payload.get_payload()
        return self._run_payload(payload_serialized, endpoint)

    def _run_payload(self, payload: Dict[str, Any], endpoint: str) -> List[RESPONSE_T]:
        """Execute a given payload. No conversion is done on the payload."""

        # Construct the getter with a backoff, and a modified number of max tries
        @backoff.on_exception(
            backoff.expo,
            (requests.exceptions.RequestException, DuplaApiException),
            max_tries=self.max_tries,
        )
        def _getter():
            response = self.get(endpoint, params=payload)
            response.raise_for_status()

            try:
                response_json: Dict[str, Any] = response.json()

                # Perform simple type check to fail fast if the server has returned
                # something unknown.
                data = response_json["data"]
                if not isinstance(data, list):
                    logger.exception(
                        "Received an invalid response from DUPLA, which was not a list: %s", data
                    )
                    raise DuplaResponseException(
                        "Invalid response from DUPLA. The data key did not contain a list.",
                        response=response,
                    )
                return data
            except DuplaResponseException as e:
                # Let the inner exception through
                raise e
            except Exception as e:
                logger.exception("Error occurred while processing response: %s", response.content)
                raise DuplaResponseException(
                    "An error occurred while parsing the DUPLA response.",
                    response=response,
                ) from e

        return _getter()
