"""This module defines the DUPLA API endpoint objects."""
from typing import Dict
from .endpoint import DuplaEndpointApiBase, DuplaApiKeys

__all__ = [
    "DuplaKtrApi",
    "DuplaLigApi",
    "DuplaMomsApi",
    "DuplaKtrObsApi",
    "DuplaLonsumApi",
    "DuplaSelskabSambeskatningApi",
    "DuplaSelskabSelvangivelseApi",
]


class DuplaKtrApi(DuplaEndpointApiBase):
    """An API client for Dataudstillingsplatformens (DUPLA) Kontrolregistreringer API."""

    DEFAULT_ENDPOINT = "Kontrolregistreringer/Virksomhed"
    FIELDS: Dict[str, bool] = {
        DuplaApiKeys.CVR: False,
        DuplaApiKeys.SE: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_FRA: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_TIL: False,
    }


class DuplaKtrObsApi(DuplaEndpointApiBase):
    """An API client for Dataudstillingsplatformens (DUPLA) Kontrolobservationer API."""

    DEFAULT_ENDPOINT: str = "Kontrolobservationer"
    FIELDS: Dict[str, bool] = {
        DuplaApiKeys.CPR: True,
        DuplaApiKeys.TEKNISK_REGISTRERING_FRA: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_TIL: False,
    }


class DuplaLigApi(DuplaEndpointApiBase):
    """An API client for Dataudstillingsplatformens (DUPLA) Ligningssager API."""

    DEFAULT_ENDPOINT: str = "Ligningssager"
    FIELDS: Dict[str, bool] = {
        DuplaApiKeys.CVR: False,
        DuplaApiKeys.SE: False,
        DuplaApiKeys.CPR: False,
        DuplaApiKeys.SAG_TYPE_KODE: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_FRA: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_TIL: False,
    }


class DuplaMomsApi(DuplaEndpointApiBase):
    """An API client for Dataudstillingsplatformens (DUPLA) Momsangivelser API."""

    DEFAULT_ENDPOINT: str = "Momsangivelse"
    FIELDS: Dict[str, bool] = {
        DuplaApiKeys.SE: True,
        DuplaApiKeys.AFREGNING_START: True,
        DuplaApiKeys.AFREGNING_SLUT: True,
        DuplaApiKeys.UDSTILLING_FRA: False,
        DuplaApiKeys.UDSTILLING_TIL: False,
    }


class DuplaLonsumApi(DuplaEndpointApiBase):
    """An API client for Dataudstillingsplatformens (DUPLA) Lønsumsangivelser API."""

    DEFAULT_ENDPOINT: str = "Lønsumsangivelser"
    FIELDS: Dict[str, bool] = {
        DuplaApiKeys.SE: True,
        DuplaApiKeys.ANGIVELSE_GYLDIG_FRA: False,
        DuplaApiKeys.ANGIVELSE_GYLDIG_TIL: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_FRA: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_TIL: False,
    }


class DuplaSelskabSambeskatningApi(DuplaEndpointApiBase):
    """An API client for Dataudstillingsplatformens (DUPLA) Selskabsambeskatningskreds API."""

    DEFAULT_ENDPOINT: str = "Selskabsskatteoplysninger/Selskabsambeskatningskreds"
    FIELDS: Dict[str, bool] = {
        DuplaApiKeys.CVR: False,
        DuplaApiKeys.SE: False,
        DuplaApiKeys.SELVANGIVESE_INDKOMST_AAR: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_FRA: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_TIL: False,
    }


class DuplaSelskabSelvangivelseApi(DuplaEndpointApiBase):
    """An API client for Dataudstillingsplatformens (DUPLA) Selskabselvangivelse API."""

    DEFAULT_ENDPOINT: str = "Selskabsskatteoplysninger/Selskabselvangivelse"
    FIELDS: Dict[str, bool] = {
        DuplaApiKeys.CVR: False,
        DuplaApiKeys.SE: False,
        DuplaApiKeys.SELVANGIVESE_INDKOMST_AAR: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_FRA: False,
        DuplaApiKeys.TEKNISK_REGISTRERING_TIL: False,
    }
