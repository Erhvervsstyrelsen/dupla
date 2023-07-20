import uuid
from datetime import date, datetime, timedelta
from typing import Type

import pytest

import dupla as dp

ALL_ENDPOINTS = (
    dp.DuplaKtrApi,
    dp.DuplaLigApi,
    dp.DuplaMomsApi,
    dp.DuplaKtrObsApi,
    dp.DuplaLonsumApi,
    dp.DuplaSelskabSambeskatningApi,
    dp.DuplaSelskabSelvangivelseApi,
)


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


def build_dummy_payload(api):
    k = dp.DuplaApiKeys  # Alias
    to_date = datetime.now()
    from_date = to_date - timedelta(days=2 * 365)
    # Dummy datas
    data = {
        k.CVR: ["12345678", 12345678],
        k.SE: ["98765432"],
        k.CPR: ["0000000000"],
        k.AFREGNING_START: from_date,
        k.AFREGNING_SLUT: to_date,
        k.UDSTILLING_FRA: from_date,
        k.UDSTILLING_TIL: to_date,
        k.TEKNISK_REGISTRERING_FRA: from_date,
        k.TEKNISK_REGISTRERING_TIL: to_date,
    }
    payload = {key: data[key] for key in api.FIELDS if key in data}
    return payload


@pytest.mark.parametrize("api", ALL_ENDPOINTS)
def test_fields_available(api):
    assert isinstance(api.FIELDS, dict)
    assert len(api.FIELDS) > 0

    # Verify that all the default fields correspond to a key defined in
    # the DuplaApiKeys class
    all_values = set(dp.DuplaApiKeys.get_all_fields().values())
    assert len(set(api.FIELDS.keys()) - all_values) == 0


@pytest.mark.parametrize("api", ALL_ENDPOINTS)
def test_build_endpoint_url(api):
    base_url = r"https://dummy.com"
    result = api.endpoint_from_base_url(base_url)
    assert isinstance(result, str)
    assert len(result) > len(base_url)
    assert result.startswith(base_url)


def test_base_endpoint_url():
    with pytest.raises(ValueError):
        dp.DuplaEndpointApiBase.endpoint_from_base_url(r"https://dummy.com")


@pytest.mark.parametrize(
    "base_url",
    [
        r"https://api.skat.dk",
        r"https://api.tfe.skat.dk",
    ],
)
def test_moms_endpoint_url_build(base_url):
    cls = dp.DuplaMomsApi
    result = cls.endpoint_from_base_url(base_url)
    assert result == base_url + r"/Momsangivelse"


@pytest.mark.parametrize("api_factory", ALL_ENDPOINTS)
def test_validate_empty_payload(api_factory):
    api = build_dummy_api(api_factory)
    # Check if the API has any required fields
    has_required = any(api.FIELDS.values())
    payload = {}
    if has_required:
        # Try testing an empty layload
        with pytest.raises(dp.InvalidPayloadException):
            api.validate_payload(payload)
    else:
        api.validate_payload(payload)


@pytest.mark.parametrize("api_factory", ALL_ENDPOINTS)
def test_validate_payload(api_factory):
    # Build a "nearly"-valid payload
    payload = build_dummy_payload(api_factory)
    payload["_INVALID_KEY_"] = 123

    # Check the "unknown" field raises an exception
    api = build_dummy_api(api_factory, allow_unknown_fields=False)

    with pytest.raises(dp.InvalidPayloadException):
        api.validate_payload(payload)

    # Now we allow unknown fields, so we shouldn't raise an error.
    # All required fields are filled in with dummy data.
    api = build_dummy_api(api_factory, allow_unknown_fields=True)
    api.validate_payload(payload)


@pytest.mark.parametrize("api_factory", ALL_ENDPOINTS)
def test_get_payload(api_factory):
    api = build_dummy_api(api_factory)
    payload_kwargs = build_dummy_payload(api)
    payload = api.get_payload(**payload_kwargs)

    assert len(payload) > 0
    assert payload_kwargs.keys() == payload.keys()

    # Test some type conversions
    for k in payload:
        v_built = payload_kwargs[k]
        v_result = payload[k]

        # Validate all date/datetime objects are converted to strings
        if isinstance(v_built, (datetime, date)):
            assert isinstance(v_result, str)


@pytest.mark.parametrize(
    "name, value, exp_type",
    [
        (dp.DuplaApiKeys.AFREGNING_START, datetime.now(), str),
        (dp.DuplaApiKeys.ANGIVELSE_GYLDIG_FRA, datetime.now(), str),
        # Should not touch these
        (dp.DuplaApiKeys.CVR, 123, int),
        (dp.DuplaApiKeys.CVR, [123], list),
    ],
)
def test_type_conversion(name, value, exp_type):
    api = build_dummy_api(dp.DuplaKtrApi)
    result = api.format_value(name, value)
    assert isinstance(result, exp_type)


@pytest.mark.parametrize("api_factory", ALL_ENDPOINTS)
def test_validate_no_auth(api_factory, mocker):
    api = build_dummy_api(api_factory)
    authentication_spy = mocker.spy(api, "_authenticate")

    payload_kwargs = build_dummy_payload(api)

    assert authentication_spy.call_count == 0
    api.get_payload(**payload_kwargs)
    assert authentication_spy.call_count == 0
