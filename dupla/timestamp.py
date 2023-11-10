from datetime import datetime, timezone


def as_utc(ts: datetime) -> datetime:
    return ts.astimezone(timezone.utc)


def as_utc_str(ts: datetime) -> str:
    return as_utc(ts).strftime("%Y-%m-%dT%H:%M:%SZ")
