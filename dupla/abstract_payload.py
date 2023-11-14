import abc
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from .api_keys import DuplaApiKeys
from .timestamp import as_utc_str

ALIAS_MAPPING: Dict[str, str] = {
    "default_endpoint": "default_endpoint",
    "se": DuplaApiKeys.SE,
    "cvr": DuplaApiKeys.CVR,
    "cpr": DuplaApiKeys.CPR,
    "registrering_fra": DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
    "registrering_til": DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
    "afregning_start": DuplaApiKeys.AFREGNING_START,
    "afregning_slut": DuplaApiKeys.AFREGNING_SLUT,
    "sag_type_kode": DuplaApiKeys.SAG_TYPE_KODE,
    "selvangivelse_aar": DuplaApiKeys.SELVANGIVESE_INDKOMST_AAR,
    "angivelse_fra": DuplaApiKeys.ANGIVELSE_GYLDIG_FRA,
    "angivelse_til": DuplaApiKeys.ANGIVELSE_GYLDIG_TIL,
    "udstilling_fra": DuplaApiKeys.UDSTILLING_FRA,
    "udstilling_til": DuplaApiKeys.UDSTILLING_TIL,
}


def _get_alias(name: str) -> str | None:
    """Get the mapping between the Pydantic field name and the Dupla key name."""
    return ALIAS_MAPPING.get(name, name)


class BasePayload(BaseModel, abc.ABC):
    """Base Payload Pydantic model"""

    model_config = ConfigDict(alias_generator=_get_alias, populate_by_name=True, extra="forbid")

    @property
    @abc.abstractmethod
    def default_endpoint(self) -> str:
        """The default endpoint for the payload"""
        # Solution from: https://github.com/pydantic/pydantic/discussions/2410#discussioncomment-408613

    def get_payload(self) -> Dict[str, Any]:
        """Get the payload in a json-able format.
        Excludes None values."""
        return self.model_dump(
            mode="json",
            exclude={"default_endpoint"},
            by_alias=True,
            exclude_none=True,
        )

    @classmethod
    def endpoint_from_base_url(cls, base_url: str) -> str:
        if not cls.default_endpoint:
            raise ValueError(f"The API {cls.__name__} has not set the default endpoint.")
        return urljoin(base_url, cls.default_endpoint)


class UdstillingMixin(BaseModel, abc.ABC):
    model_config = ConfigDict(alias_generator=_get_alias, populate_by_name=True, extra="forbid")

    udstilling_fra: Optional[datetime] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.UDSTILLING_FRA,
    )
    udstilling_til: Optional[datetime] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.UDSTILLING_TIL,
    )

    @field_serializer("udstilling_fra")
    @field_serializer("udstilling_til")
    def serialize_udstilling(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return dt
        return as_utc_str(dt)
