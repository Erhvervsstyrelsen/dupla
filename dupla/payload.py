import abc
from datetime import date, datetime
from typing import Annotated, Any, ClassVar, Dict, List, Optional, TypeAlias
from urllib.parse import urljoin

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_serializer

from .api_keys import DuplaApiKeys
from .timestamp import as_utc_str


def _string_num_len_n(n: int) -> str:
    """Helper function to validate the correctness
    of integer-like strings. The length of the string is checked."""

    def _inner(s: str):
        try:
            int(s)  # Verify the number is int-like
        except ValueError:
            raise ValueError(f"Number must be integer-like, got {s!r}") from None
        if len(s) != n:
            raise ValueError(f"Must of length {n}.")
        return s

    return _inner


CVR_STR = Annotated[str, AfterValidator(_string_num_len_n(8))]
SE_STR = Annotated[str, AfterValidator(_string_num_len_n(8))]
CPR_STR = Annotated[str, AfterValidator(_string_num_len_n(10))]

CVR_T: TypeAlias = List[CVR_STR]
CPR_T: TypeAlias = List[CPR_STR]
SE_T: TypeAlias = List[SE_STR]

ENDP_T = ClassVar[str]

ALIAS_DCT: Dict[str, str] = {
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
}


def get_alias(name: str) -> str:
    return ALIAS_DCT[name]


class BasePayload(BaseModel, abc.ABC):
    """Base Payload Pydantic model"""

    model_config = ConfigDict(alias_generator=get_alias, populate_by_name=True, extra="forbid")

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


class UdstillingMixin(BaseModel):
    model_config = ConfigDict(alias_generator=get_alias, populate_by_name=True, extra="forbid")

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


class KtrPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Kontrolregistreringer API."""

    default_endpoint: ENDP_T = "Kontrolregistreringer/Virksomhed"

    cvr: Optional[CVR_T] = Field(default=None)
    se: Optional[SE_T] = Field(default=None)
    registrering_fra: Optional[date] = Field(default=None)
    registrering_til: Optional[date] = Field(default=None)


class KtrObsPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Kontrolobservationer API."""

    default_endpoint: ENDP_T = "Kontrolobservationer"

    cpr: CPR_T = Field()
    registrering_fra: Optional[date] = Field(default=None)
    registrering_til: Optional[date] = Field(default=None)


class LigPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Ligningssager API."""

    default_endpoint: ENDP_T = "Ligningssager"

    cvr: Optional[CVR_T] = Field(default=None)
    se: Optional[SE_T] = Field(default=None)
    cpr: Optional[CPR_T] = Field(default=None)

    sag_type_kode: Optional[str] = Field(default=None)

    registrering_fra: Optional[date] = Field(default=None)
    registrering_til: Optional[date] = Field(default=None)


class MomsPayload(BasePayload, UdstillingMixin):
    """An API client for Dataudstillingsplatformens (DUPLA) Momsangivelser API."""

    default_endpoint: ENDP_T = "Momsangivelse"
    se: SE_T = Field()
    afregning_start: date = Field()
    afregning_slut: date = Field()


class LonsumPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Lønsumsangivelser API."""

    default_endpoint: ENDP_T = "Lønsumsangivelser"
    se: SE_T = Field()

    registrering_fra: Optional[date] = Field(default=None)
    registrering_til: Optional[date] = Field(default=None)

    angivelse_fra: Optional[date] = Field(default=None)
    angivelse_til: Optional[date] = Field(default=None)


class SelskabSambeskatningPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Selskabsambeskatningskreds API."""

    default_endpoint: ENDP_T = "Selskabsskatteoplysninger/Selskabsambeskatningskreds"
    cvr: Optional[CVR_T] = Field(default=None)
    se: Optional[SE_T] = Field(default=None)

    selvangivelse_aar: Optional[str] = Field(default=None)
    registrering_fra: Optional[date] = Field(default=None)
    registrering_til: Optional[date] = Field(default=None)


class SelskabSelvangivelse(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Selskabselvangivelse API."""

    default_endpoint: ENDP_T = "Selskabsskatteoplysninger/Selskabselvangivelse"

    cvr: Optional[CVR_T] = Field(default=None)
    se: Optional[SE_T] = Field(default=None)

    selvangivelse_aar: Optional[str] = Field(default=None)
    registrering_fra: Optional[date] = Field(default=None)
    registrering_til: Optional[date] = Field(default=None)
