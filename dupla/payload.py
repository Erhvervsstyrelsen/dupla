from datetime import date
from typing import ClassVar, Optional

from pydantic import Field

from .abstract_payload import BasePayload, UdstillingMixin
from .custom_types import CPR_T, CVR_T, SE_T

ENDP_T = ClassVar[str]


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
