import random
import uuid
from datetime import timedelta
from typing import Type

import pytest
from faker import Faker
from pydantic import BaseModel

import dupla as dp

ALL_PAYLOADS = (
    dp.payload.KtrPayload,
    dp.payload.LigPayload,
    dp.payload.MomsPayload,
    dp.payload.KtrObsPayload,
    dp.payload.LonsumPayload,
    dp.payload.SelskabSambeskatningPayload,
    dp.payload.SelskabSelvangivelse,
)

fake = Faker()


def build_dummy_api(
    api_factory: Type[dp.DuplaEndpointApiBase], max_tries=1, **kwargs
) -> dp.DuplaEndpointApiBase:
    endpoint = api_factory.endpoint_from_base_url(r"https://dummy.com")
    api = api_factory(
        endpoint,
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        "pkcs12_filename",
        "pkcs12_password",
        "http://billetautomat.dk/url",
        5,
        max_tries=max_tries,
        **kwargs,
    )
    return api


def get_fake_cvr():
    return fake.numerify("#" * 8)


def get_fake_se():
    return get_fake_cvr()


def get_fake_cpr():
    return fake.numerify("#" * 10)


def build_dummy_payload(api: Type[BaseModel]):
    k = dp.DuplaApiKeys  # Alias

    to_datetime = fake.date_time()
    from_datetime = to_datetime - timedelta(days=random.randint(1, 2 * 365))

    to_date = fake.date_object()
    from_date = to_date - timedelta(days=random.randint(1, 2 * 365))

    # Dummy datas
    data = {
        k.CVR: [get_fake_cvr() for _ in range(random.randint(1, 15))],
        k.SE: [get_fake_se() for _ in range(random.randint(1, 15))],
        k.CPR: [get_fake_cpr() for _ in range(random.randint(1, 15))],
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
    obj = dp.payload.KtrPayload(se=[get_fake_se()], registrering_fra=faker.date_object())
    payload = obj.get_payload()
    assert dp.DuplaApiKeys.SE in payload
    assert dp.DuplaApiKeys.TEKNISK_REGISTRERING_FRA in payload
    # Unspecified, should not be in the payload
    assert dp.DuplaApiKeys.CVR not in payload
    assert dp.DuplaApiKeys.TEKNISK_REGISTRERING_TIL not in payload
    assert "default_endpoint" not in payload
