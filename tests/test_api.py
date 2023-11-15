import random
import uuid
from datetime import date, datetime, timedelta
from typing import Type

import pytest
from faker import Faker
from pydantic import BaseModel, ValidationError

import dupla as dp
from dupla.api_keys import DuplaApiKeys
from dupla.timestamp import TZ_UTC

ALL_PAYLOADS: tuple[Type[dp.payload.BasePayload]] = (
    dp.payload.KtrPayload,
    dp.payload.LigPayload,
    dp.payload.MomsPayload,
    dp.payload.KtrObsPayload,
    dp.payload.LonsumPayload,
    dp.payload.SelskabSambeskatningPayload,
    dp.payload.SelskabSelvangivelse,
)

fake = Faker()


def build_dummy_api(max_tries=1, **kwargs) -> dp.DuplaAccess:
    api = dp.DuplaAccess(
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        "pkcs12_filename",
        "pkcs12_password",
        r"http://billetautomat.dk/url",
        max_tries=max_tries,
        jwt_token_expiration_overlap=5,
        base_url=r"https://dummy.com",
        **kwargs,
    )
    return api


def get_num_of_len(n: int = 1):
    return fake.numerify("#" * n)


def get_fake_cvr(n=1):
    return [get_num_of_len(8) for _ in range(n)]


def get_fake_se(n=1):
    return get_fake_cvr(n=n)


def get_fake_cpr(n=1):
    return [get_num_of_len(10) for _ in range(n)]


def build_dummy_payload(api: Type[BaseModel]):
    k = dp.DuplaApiKeys  # Alias

    to_datetime = fake.date_time()
    from_datetime = to_datetime - timedelta(days=random.randint(1, 2 * 365))

    to_date = fake.date_object()
    from_date = to_date - timedelta(days=random.randint(1, 2 * 365))

    # Dummy datas
    data = {
        k.CVR: get_fake_cvr(n=random.randint(1, 15)),
        k.SE: get_fake_se(n=random.randint(1, 15)),
        k.CPR: get_fake_cpr(n=random.randint(1, 15)),
        k.AFREGNING_START: from_date,
        k.AFREGNING_SLUT: to_date,
        k.UDSTILLING_FRA: from_datetime,
        k.UDSTILLING_TIL: to_datetime,
        k.TEKNISK_REGISTRERING_FRA: from_date,
        k.TEKNISK_REGISTRERING_TIL: to_date,
        k.SELVANGIVESE_INDKOMST_AAR: str(random.randint(1970, 2050)),
    }

    def key_val_iter(api):
        for k, v in api.model_fields.items():
            key = k
            if v.alias:
                key = v.alias
            if key not in data:
                continue
            val = data[key]
            yield key, val

    payload = {key: val for key, val in key_val_iter(api) if key in data}
    return api(**payload)


@pytest.mark.parametrize("api", ALL_PAYLOADS)
def test_dummy_payload(api):
    m = build_dummy_payload(api)
    # Try building the payload
    payload = m.get_payload()
    assert "default_endpoint" not in payload


def test_get_payload(faker):
    to_date = faker.date_object()
    obj = dp.payload.KtrPayload(se=get_fake_se(), registrering_fra=to_date)
    payload = obj.get_payload()
    assert isinstance(payload, dict)
    assert all(isinstance(k, str) for k in payload.keys())
    assert DuplaApiKeys.SE in payload
    assert DuplaApiKeys.TEKNISK_REGISTRERING_FRA in payload
    # Unspecified, should not be in the payload
    assert DuplaApiKeys.CVR not in payload
    assert DuplaApiKeys.TEKNISK_REGISTRERING_TIL not in payload
    assert "default_endpoint" not in payload

    val = payload[dp.DuplaApiKeys.TEKNISK_REGISTRERING_FRA]
    assert isinstance(val, str)
    assert val == str(to_date)
    assert datetime.fromisoformat(val).date() == to_date


def test_payload_bad_arg(faker):
    with pytest.raises(ValidationError):
        dp.payload.KtrPayload(se=get_fake_se(), hello="123")


@pytest.mark.parametrize(
    "base_url",
    [
        r"https://api.skat.dk",
        r"https://api.tfe.skat.dk",
    ],
)
def test_moms_endpoint_url_build(base_url):
    cls = dp.payload.MomsPayload
    result = cls.endpoint_from_base_url(base_url)
    assert cls.default_endpoint == "Momsangivelse"
    assert r"/Momsangivelse" in result
    assert result == base_url + r"/Momsangivelse"


@pytest.mark.parametrize("payload", ALL_PAYLOADS)
@pytest.mark.parametrize(
    "base_url",
    [
        r"https://api.skat.dk",
        r"https://api.tfe.skat.dk",
    ],
)
def test_endpoint_url_build(base_url, payload: Type[dp.payload.BasePayload]):
    result = payload.endpoint_from_base_url(base_url)
    assert payload.default_endpoint in result
    assert result == base_url + r"/" + payload.default_endpoint


@pytest.mark.parametrize("as_iso", [False, True])
def test_moms_datetime(faker, as_iso: bool):
    """Test some date/datetime conversion"""
    for _ in range(20):
        # Repeat the test a few times with different dates
        dt: datetime = faker.date_time(tzinfo=TZ_UTC)
        obj = dp.payload.MomsPayload(
            se=get_fake_se(),
            udstilling_til=dt.isoformat() if as_iso else dt,
            afregning_start=dt.date(),
            afregning_slut=dt.date(),
        )

        assert obj.udstilling_til == dt
        payload = obj.get_payload()
        assert DuplaApiKeys.UDSTILLING_TIL in payload
        assert datetime.fromisoformat(payload[DuplaApiKeys.UDSTILLING_TIL]) == dt

        assert isinstance(payload[DuplaApiKeys.AFREGNING_START], str)
        assert payload[DuplaApiKeys.AFREGNING_START] == str(dt.date())


@pytest.mark.parametrize("payload_cls", ALL_PAYLOADS)
def test_api_builds_payload(payload_cls, mocker):
    spy = mocker.spy(payload_cls, "get_payload")
    spy2 = mocker.spy(payload_cls, "endpoint_from_base_url")
    api = build_dummy_api()
    obj = build_dummy_payload(payload_cls)
    assert spy.call_count == 0
    assert spy2.call_count == 0
    api.get_data(obj)
    assert spy.call_count == 1
    assert spy2.call_count == 1


@pytest.mark.parametrize("str_len", [0, 1, 2, 7, 9, 10])
def test_invalid_se(str_len: int):
    with pytest.raises(ValidationError):
        dp.payload.KtrPayload(se=[get_num_of_len(n=str_len)])
    dp.payload.KtrPayload(se=[get_num_of_len(n=8)])


def test_other_invalid_se():
    dp.payload.KtrPayload(se=[get_num_of_len(n=8)])
    with pytest.raises(ValidationError):
        dp.payload.KtrPayload(se=["a" * 8])


@pytest.mark.parametrize(
    "input",
    [
        ["12345678"],
        [12345678, 87654321],
        ["12345678", 12345678],
    ],
)
def test_int_or_string(input):
    dp.payload.KtrPayload(se=input)


def test_mom_udstilling(faker):
    payload = {
        DuplaApiKeys.SE: get_fake_se(n=5),
        DuplaApiKeys.AFREGNING_START: "1970-01-01",
        DuplaApiKeys.AFREGNING_SLUT: date.today(),
        DuplaApiKeys.UDSTILLING_FRA: faker.date_time(tzinfo=TZ_UTC),
        DuplaApiKeys.UDSTILLING_TIL: faker.date_time(tzinfo=TZ_UTC),
    }
    m = dp.payload.MomsPayload(**payload)
    assert isinstance(m, dp.payload.MomsPayload)
    assert isinstance(m.udstilling_til, datetime)
    assert isinstance(m.udstilling_fra, datetime)

    dct = m.get_payload()
    for key in [DuplaApiKeys.UDSTILLING_FRA, DuplaApiKeys.UDSTILLING_TIL]:
        assert isinstance(dct[key], str)
        fmt = datetime.fromisoformat(dct[key])
        exp = payload[key]
        assert fmt == exp
