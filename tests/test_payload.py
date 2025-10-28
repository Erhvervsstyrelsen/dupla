from datetime import date, datetime

import pytest
from pydantic import ValidationError

from dupla.abstract_payload import BasePayload
from dupla.api_keys import DuplaApiKeys
from dupla.custom_types import CPR_T, CVR_T, SE_T
from dupla.payload import ENDP_T


class DummyBase(BasePayload):
    default_endpoint: ENDP_T = "dummy"


class DummySE(DummyBase):
    se: SE_T


class DummyCVR(DummyBase):
    cvr: CVR_T


class DummyCPR(DummyBase):
    cpr: CPR_T


class DummyDate(DummyBase):
    dt: date


class DummyDatetime(DummyBase):
    dt: datetime


def test_dummy_base():
    DummyBase()


@pytest.mark.parametrize(
    "input",
    [
        ["12345678"],
        [12345678, 87654321],
        ["12345678", 12345678],
    ],
)
@pytest.mark.parametrize("key", ["se", DuplaApiKeys.SE])
def test_int_se_conversion(input, key: str):
    kwargs = {key: input}
    inst = DummySE(**kwargs)
    assert len(inst.se) == len(input)
    assert all(isinstance(val, str) for val in inst.se)


@pytest.mark.parametrize(
    "input",
    [
        ["12345678"],
        [12345678, 87654321],
        ["12345678", 12345678],
    ],
)
@pytest.mark.parametrize("key", ["cvr", DuplaApiKeys.CVR])
def test_int_cvr_conversion(input, key):
    kwargs = {key: input}
    inst = DummyCVR(**kwargs)
    assert len(inst.cvr) == len(input)
    assert all(isinstance(val, str) for val in inst.cvr)


@pytest.mark.parametrize(
    "input",
    [
        ["1234567890"],
        [3103923289, 9876543210],
        ["1234567890", 1234567890],
    ],
)
@pytest.mark.parametrize("key", ["cpr", DuplaApiKeys.CPR])
def test_int_cpr_conversion(input, key):
    kwargs = {key: input}
    inst = DummyCPR(**kwargs)
    assert len(inst.cpr) == len(input)
    assert all(isinstance(val, str) for val in inst.cpr)


@pytest.mark.parametrize(
    "val",
    [
        "2023-10-01",
        date(year=2020, month=10, day=1),
    ],
)
def test_dummy_date(val):
    obj = DummyDate(dt=val)
    assert isinstance(obj.dt, date)


@pytest.mark.parametrize(
    "val",
    [
        "2023/10/03",
        "2023-10-01T20:00:00",
        "2023-10-01T20:00:00+00:00",
        "2023-10-01T20:00:00+01:00",
        "2023-10-01T20:00:00+02:00",
    ],
)
def test_invalid_date(val):
    with pytest.raises(ValidationError):
        DummyDate(dt=val)


@pytest.mark.parametrize(
    "val",
    [
        datetime.fromisoformat("2023-10-01T20:00:00+02:00"),
        "2023-10-01T20:00:00+02:00",
        "1900-01-01T20:00:00+00:00",
        date(year=2020, month=10, day=1),
    ],
)
def test_datetime(val):
    obj = DummyDatetime(dt=val)
    assert isinstance(obj.dt, datetime)


@pytest.mark.parametrize(
    "val",
    [
        "2023-13-01",
        "2023-10-32",
        "2023/10/03",
    ],
)
def test_invalid_datetime(val):
    with pytest.raises(ValidationError):
        DummyDatetime(dt=val)
