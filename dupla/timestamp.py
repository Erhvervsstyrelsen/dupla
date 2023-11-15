import zoneinfo
from datetime import datetime

TZ_UTC = zoneinfo.ZoneInfo("UTC")
TZ_DK = zoneinfo.ZoneInfo("Europe/Copenhagen")


def get_utc_now() -> datetime:
    return datetime.now(tz=TZ_UTC)


def get_dk_now() -> datetime:
    return datetime.now(tz=TZ_DK)


def as_utc(ts: datetime) -> datetime:
    return ts.astimezone(TZ_UTC)
