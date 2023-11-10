from datetime import date, datetime
from typing import Any, Dict, List, Optional, TypeAlias

from pydantic import BaseModel, Field, field_serializer

from .endpoint import DuplaApiKeys
from .timestamp import as_utc_str

CVR_T: TypeAlias = List[str]
CPR_T: TypeAlias = List[str]
SE_T: TypeAlias = List[str]


class BasePayload(BaseModel):
    """Base Payload Pydantic model"""

    default_endpoint: str = ""

    def get_payload(self) -> Dict[str, Any]:
        """Get the payload in a json-able format.
        Excludes None values."""
        return self.model_dump(
            mode="json",
            exclude={"default_endpoint"},
            by_alias=True,
            exclude_none=True,
        )


class UdstillingMixin(BaseModel):
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

    default_endpoint: str = "Kontrolregistreringer/Virksomhed"

    cvr: Optional[CVR_T] = Field(default=None, serialization_alias=DuplaApiKeys.CVR)
    se: Optional[SE_T] = Field(default=None, serialization_alias=DuplaApiKeys.SE)
    registrering_fra: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
    )
    registrering_til: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
    )


class KtrObsPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Kontrolobservationer API."""

    default_endpoint: str = "Kontrolobservationer"

    cpr: CPR_T = Field(serialization_alias=DuplaApiKeys.CPR)
    registrering_fra: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
    )
    registrering_til: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
    )


class LigPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Ligningssager API."""

    default_endpoint: str = "Ligningssager"

    cvr: Optional[CVR_T] = Field(default=None, serialization_alias=DuplaApiKeys.CVR)
    se: Optional[SE_T] = Field(default=None, serialization_alias=DuplaApiKeys.SE)
    cpr: Optional[CPR_T] = Field(default=None, serialization_alias=DuplaApiKeys.CPR)

    sag_type_kode: Optional[str] = Field(
        default=None, serialization_alias=DuplaApiKeys.SAG_TYPE_KODE
    )

    registrering_fra: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
    )
    registrering_til: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
    )


class MomsPayload(BasePayload, UdstillingMixin):
    """An API client for Dataudstillingsplatformens (DUPLA) Momsangivelser API."""

    default_endpoint: str = "Momsangivelse"
    se: List[str] = Field(serialization_alias=DuplaApiKeys.SE)
    afregning_start: date = Field(serialization_alias=DuplaApiKeys.AFREGNING_START)
    afregning_slut: date = Field(serialization_alias=DuplaApiKeys.AFREGNING_SLUT)


class LonsumPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Lønsumsangivelser API."""

    default_endpoint: str = "Lønsumsangivelser"
    se: List[str] = Field(serialization_alias=DuplaApiKeys.SE)

    registrering_fra: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
    )
    registrering_til: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
    )

    angivelse_fra: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.ANGIVELSE_GYLDIG_FRA,
    )
    angivelse_til: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.ANGIVELSE_GYLDIG_TIL,
    )


class SelskabSambeskatningPayload(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Selskabsambeskatningskreds API."""

    default_endpoint: str = "Selskabsskatteoplysninger/Selskabsambeskatningskreds"
    cvr: Optional[CVR_T] = Field(default=None, serialization_alias=DuplaApiKeys.CVR)
    se: Optional[SE_T] = Field(default=None, serialization_alias=DuplaApiKeys.SE)

    selvangivelse_aar: Optional[str] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.SELVANGIVESE_INDKOMST_AAR,
    )
    registrering_fra: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
    )
    registrering_til: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
    )


class SelskabSelvangivelse(BasePayload):
    """An API client for Dataudstillingsplatformens (DUPLA) Selskabselvangivelse API."""

    default_endpoint: str = "Selskabsskatteoplysninger/Selskabselvangivelse"

    cvr: Optional[CVR_T] = Field(default=None, serialization_alias=DuplaApiKeys.CVR)
    se: Optional[SE_T] = Field(default=None, serialization_alias=DuplaApiKeys.SE)

    selvangivelse_aar: Optional[str] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.SELVANGIVESE_INDKOMST_AAR,
    )
    registrering_fra: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_FRA,
    )
    registrering_til: Optional[date] = Field(
        default=None,
        serialization_alias=DuplaApiKeys.TEKNISK_REGISTRERING_TIL,
    )
