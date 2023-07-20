from datetime import date, datetime
from typing import Union

ISO_FMT = "%Y-%m-%d"  # Date format for fields requiring yyyy-mm-dd


def convert_and_validate_iso_date(value: Union[str, date, datetime]) -> str:
    """Convert a date/datetime object to ISO.
    The value is validated to be a valid yyyy-mm-dd date string."""
    if isinstance(value, (date, datetime)):
        value = value.strftime(ISO_FMT)
    if not validate_iso_date(value):
        raise ValueError(f"Date '{value}' is not a date of the format yyyy-mm-dd")
    return value


def validate_iso_date(date: str) -> bool:
    """Verify that a date string has a valid correct yyyy-mm-dd format"""
    try:
        datetime.strptime(date, ISO_FMT)
    except ValueError:
        return False
    return True
