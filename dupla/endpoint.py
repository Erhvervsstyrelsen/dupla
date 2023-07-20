import logging
from dataclasses import dataclass, fields
from datetime import date, datetime
from typing import Any, Dict, List
from urllib.parse import urljoin

import backoff
import requests

from .base import DuplaApiBase
from .exceptions import DuplaApiException, DuplaResponseException, InvalidPayloadException
from .validation import convert_and_validate_iso_date

logger = logging.getLogger(__file__)

__all__ = ["DuplaEndpointApiBase", "DuplaApiKeys"]

RESPONSE_T = Dict[str, Any]


@dataclass
class DuplaApiKeys:
    """Container for DUPLA API keys."""

    CVR: str = "VirksomhedCVRNummer"
    SE: str = "VirksomhedSENummer"
    CPR: str = "PersonCPRNummer"

    TEKNISK_REGISTRERING_FRA: str = "TekniskRegistreringDatoFra"
    TEKNISK_REGISTRERING_TIL: str = "TekniskRegistreringDatoTil"

    AFREGNING_START: str = "AfregningPeriodeForholdPeriodeStartDato"
    AFREGNING_SLUT: str = "AfregningPeriodeForholdPeriodeSlutDato"

    UDSTILLING_FRA: str = "UdstillingRegistreringFra"
    UDSTILLING_TIL: str = "UdstillingRegistreringTil"

    ANGIVELSE_GYLDIG_FRA: str = "AngivelseGyldigDatoFra"
    ANGIVELSE_GYLDIG_TIL: str = "AngivelseGyldigDatoTil"

    SELVANGIVESE_INDKOMST_AAR: str = "SelskabSelvangivelseIndkomstÅr"

    SAG_TYPE_KODE: str = "SagTypeKode"

    @classmethod
    def get_all_field_names(cls) -> List[str]:
        """Get all of the available attributes."""
        return [f.name for f in fields(cls)]

    @classmethod
    def get_all_fields(cls) -> Dict[str, str]:
        """Get a dictionary mapping the class attributes to the attribute values."""
        return {f: getattr(cls, f) for f in cls.get_all_field_names()}


class DuplaEndpointApiBase(DuplaApiBase):
    """
    Endpoint class for API acces to the Dataudveklspingsplatformen API (Dupla).

    Child classes inheriting from this class should specify their API specifications and
    whether a field is required in the FIELDS dictionary.

    Attributes:
        FIELDS: A dictionary of the allowed fields by the SKAT schema, and whether it is
            required. Must be populated by the child class.
        DEFAULT_ENDPOINT: A string of the default name for the API endpoint, which is to be
            added to the base SKAT URL to construct the full endpoint URL. Must be defined
            by the child class.
        endpoint (str): The HTTP(S) endpoint of the API.
        allow_unknown_fields (bool): Whether a payload may contain fields which do not
        exist in the FIELDS dictionary.
    """

    endpoint: str
    # Dictionary of payload keys and whether they are required.
    # Defines a primitive payload schema, with no type checking.
    FIELDS: Dict[str, bool] = {}

    # The default server endpoint hos skat.dk. Should be overridden by the API endpoint child class.
    # Mainly serves as a reminder of what the endpoint at skat is,
    # and is not used directly by the class.
    DEFAULT_ENDPOINT: str = ""

    def __init__(
        self,
        endpoint: str,
        transaction_id: str,
        agreement_id: str,
        pkcs12_filename: str,
        pkcs12_password: str,
        billetautomat_url: str,
        jwt_token_expiration_overlap: int = 5,
        allow_unknown_fields: bool = False,
        max_tries: int = 8,
    ):
        """Instantiates new DUPLA API endpoint client.
        Args:
            endpoint (str): The HTTP(S) endpoint of the API.
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
            allow_unknown_fields (bool): Allow the presence of fields which are not specified in
                the endpoint FIELDS dictionary? If False, then an error is raised if the payload
                contains an unknown entry.
            max_tries (int): Maximum number of times a failed request is re-attempted in
                ``get_data``. Defaults to 8.
        """

        self.endpoint = endpoint
        self.allow_unknown_fields = allow_unknown_fields
        self.max_tries = max_tries
        super().__init__(
            transaction_id,
            agreement_id,
            pkcs12_filename,
            pkcs12_password,
            billetautomat_url,
            jwt_token_expiration_overlap,
        )

    def get_endpoint(self) -> str:
        """Retrieve the endpoint URL."""
        return self.endpoint

    def validate_payload(self, payload: Dict[str, Any]) -> None:
        """Check if a payload is in accordance with the schema specifications.

        Raises an InvalidPayloadException if the payload is invalid.
        """
        # Check all required keys are present.
        for field, is_required in self.FIELDS.items():
            if is_required and field not in payload:
                raise InvalidPayloadException(f"Field '{field}' is missing in the payload.")

        if not self.allow_unknown_fields:
            # Verify all entries in the payload are known.
            allowed_keys = set(self.FIELDS.keys())
            found_keys = set(payload.keys())
            unknown_keys = found_keys - allowed_keys
            if unknown_keys:
                # We found at least one field which is not in the specification.
                all_fields = ", ".join(payload.keys())
                raise InvalidPayloadException(
                    f"Entries '{unknown_keys}' in the payload are unknown. "
                    f"Allowed keys: {all_fields}."
                )

    def get_payload(self, **kwargs) -> Dict[str, Any]:
        """Construct and validate the payload to be sent by the API.
        kwargs are passed directly into the payload as key-value pairs.
        """
        payload = self.build_payload(**kwargs)
        self.validate_payload(payload)
        return payload

    def format_value(self, name: str, value: Any):
        if name in [
            DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
            DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
            DuplaApiKeys.AFREGNING_START,
            DuplaApiKeys.AFREGNING_SLUT,
            DuplaApiKeys.ANGIVELSE_GYLDIG_TIL,
            DuplaApiKeys.ANGIVELSE_GYLDIG_FRA,
        ]:
            return convert_and_validate_iso_date(value)
        if name in [DuplaApiKeys.UDSTILLING_FRA, DuplaApiKeys.UDSTILLING_TIL]:
            if isinstance(value, (date, datetime)):
                return value.strftime("%Y-%m-%dT%H:%M:%SZ")
        return value

    def build_payload(self, **kwargs) -> Dict[str, Any]:
        """Format the input values of the payload."""
        return {key: self.format_value(key, value) for key, value in kwargs.items()}

    def get_data(
        self,
        payload: Dict[str, Any],
        format_payload: bool = True,
        validate_payload: bool = True,
    ) -> List[RESPONSE_T]:
        """Request the server for data.

        Args:
            payload (dict): Payload, e.g. constructed from the `get_payload` method.
            format_payload (bool, optional): Whether to call `build_payload` on the provided
                payload. Otherwise the payload is provided as-is.
                Defaults to True.
            validate_payload (bool, optional): Whether to validate the payload.
                Defaults to True.

        Returns:
            List[Dict[str, Any]]: A JSON list representing data as returned by the API.
        """

        if format_payload:
            payload = self.build_payload(**payload)
        if validate_payload:
            self.validate_payload(payload)
        return self._run_payload(payload)

    def _run_payload(self, payload: Dict[str, Any]) -> List[RESPONSE_T]:
        """Execute a given payload. No conversion is done on the payload."""

        endpoint = self.get_endpoint()

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

    @classmethod
    def endpoint_from_base_url(cls, url: str) -> str:
        if not cls.DEFAULT_ENDPOINT:
            raise ValueError(f"The API {cls.__name__} has not set the default endpoint.")
        return urljoin(url, cls.DEFAULT_ENDPOINT)
