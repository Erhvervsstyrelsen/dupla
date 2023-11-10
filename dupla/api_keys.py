from dataclasses import dataclass, fields
from typing import Dict, List

__all__ = ["DuplaApiKeys"]


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
