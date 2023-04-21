from datetime import datetime, timedelta
from uuid import uuid4
from typing import Any, Dict, Optional
import logging

import requests
import requests_pkcs12

from .exceptions import DuplaApiAuthenticationException

__all__ = [
    "DuplaApiBase",
]

logger = logging.getLogger(__file__)


class DuplaApiBase:
    """Base class for API acces to the Dataudveklspingsplatformen API (Dupla).
    Handles authentication and headers for the API requests.

    Arguments:
        transaction_id (str): An ID used to correlate requests across the API.
            Should be constant for IKP-DA.
        agreement_id (str): An ID/token supplied by the API provider.
        pkcs12_filename (str): Path to PKCS12 certificate file.
        pkcs12_password (str): Password for PKCS12 certificate file.
        billetautomat_url (str): Endpoint to the authentication service for requesting JWT tokens.
        jwt_token_expiration_overlap (int): The overlap time for token expiration time (in seconds)
            to avoid situations where token is almost expired during the check and will be rejected
            in a next request.
    """

    transaction_id: str
    agreement_id: str
    _pkcs12_adapter: requests_pkcs12.Pkcs12Adapter

    def __init__(
        self,
        transaction_id: str,
        agreement_id: str,
        pkcs12_filename: str,
        pkcs12_password: str,
        billetautomat_url: str,
        jwt_token_expiration_overlap: int,
    ):
        self.transaction_id = transaction_id
        self.agreement_id = agreement_id

        self._pkcs12_adapter = requests_pkcs12.Pkcs12Adapter(
            pkcs12_filename=pkcs12_filename,
            pkcs12_password=pkcs12_password,
        )
        self.billetautomat_url = billetautomat_url
        self.jwt_token_expiration_overlap = jwt_token_expiration_overlap
        self.token_expiration_time: Optional[datetime] = None
        self.jwt_token: Optional[str] = None

    def request(self, method, url, **kwargs) -> requests.Response:
        """Constructs and sends a `requests.Request` with appropriate headers
        (including the JWT authenticationtoken) for the Dupla API.
        If token is not present or is expired - first sends a request to the authentication
        service using mTlS connection and the set certificate to get the JWT authentication token.
        Then the token is used to authenticate requests to Dupla API until it's expired -
        then the JWT token is retrieved again.

        Arguments:
            method (str): HTTP method of the `requests.Request` object
            url (str): URL for the new :class:`Request` object.
            **kwargs (Optional[Dict]): Optional arguments that `requests.request` takes.

        Returns:
            requests.Reponse: A requests Response opject
        """
        request_id = uuid4()
        if not self._is_token_present() or self._is_token_expired():
            self._authenticate()

        headers = {
            "X-Request-ID": str(request_id),
            "X-Transaktions-ID": self.transaction_id,
            "UFST-Adgangsgrundlag": f"urn:ufst:adgangsgrundlag:aftale:{self.agreement_id}",
            "Authorization": f"Bearer {self.jwt_token}",
        }

        with requests.Session() as session:
            session.headers.update(headers)

            return session.request(method, url, **kwargs)

    def get(
        self, url: str, params: Optional[Dict] = None, **kwargs: Dict[str, Any]
    ) -> requests.Response:
        """Sends a GET request, handling authentication and API headers.

        Arguments:
            url (str): URL for the new `requests.Request` object.
            params (Optional[Dict]): Dictionary, list of tuples or bytes to send in the
                query string for the :class:`Request`.
            **kwargs (Optional[Dict]): Optional arguments that `requests.request` takes.

        Returns:
            requests.Reponse: A requests Response opject
        """
        return self.request("get", url, params=params, **kwargs)

    def _authenticate(self) -> None:
        """Retrieves a JWT token from the authentication service (billetautomat) to be used for
        Dupla API requests. The connection to the authentication service is encrypted with mTLS
        and the set certificate. To retrieve a JWT token, the payload must include 2 fields -
        client_id which is always "api-gateway" and so called "nonce" which is uuid v4 string.
        Nonce should be unique per request and can be understood as a request id.
        The token expiration time is set as well for further checks.
        """
        self.token_expiration_time = None
        self.jwt_token = None
        nonce = str(uuid4())

        payload = {"client_id": "api-gateway", "nonce": nonce}

        with requests.Session() as session:
            session.mount(self.billetautomat_url, self._pkcs12_adapter)
            result = session.post(self.billetautomat_url, json=payload)
            if result.ok:
                result_payload = result.json()
            else:
                raise DuplaApiAuthenticationException(
                    f"JWT error: fetching the token failed, "
                    f"http code: {result.status_code}, "
                    f"message: {result.content.decode()}"
                )

        if access_token := result_payload.get("access_token"):
            self.jwt_token = access_token
        else:
            raise DuplaApiAuthenticationException(
                "JWT error: access_token not present in response payload"
            )
        if expires_in := result_payload.get("expires_in"):
            self.token_expiration_time = datetime.now() + timedelta(seconds=expires_in)
        else:
            raise DuplaApiAuthenticationException(
                "JWT error: expires_in not present in response payload"
            )

    def _is_token_present(self) -> bool:
        """Checks whether the JWT token was retrieved and the expiration time is set.

        Returns:
            True if the JWT token and expiration time are set, False otherwise.
        """
        return self.jwt_token is not None and self.token_expiration_time is not None

    def _is_token_expired(self) -> bool:
        """Checks whether the JWT token is expired. To avoid situations where the token is valid
        for the last second but could be considered as expired in a next request - overlap time
        is used to consider the token as expired quicker.

        Returns:
            True if the JWT token is expired, False otherwise.
        """
        return datetime.now() >= self.token_expiration_time - timedelta(
            seconds=self.jwt_token_expiration_overlap
        )
