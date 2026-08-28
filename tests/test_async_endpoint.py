import asyncio
import uuid

import pytest

import dupla as dp
from dupla.async_endpoint import AsyncDuplaAccess
from dupla.exceptions import DuplaApiUsageException


def build_dummy_async_access(max_tries=1, **kwargs) -> AsyncDuplaAccess:
    return AsyncDuplaAccess(
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


def build_entities(n: int):
    return [dp.payload.KtrPayload(se=[10_000_000 + i]) for i in range(n)]


async def test_results_without_entities_raises():
    api = build_dummy_async_access()
    with pytest.raises(DuplaApiUsageException):
        _ = api.results


async def test_results_streams_all_entities(mocker):
    entities = build_entities(5)
    api = build_dummy_async_access()
    mocker.patch.object(AsyncDuplaAccess, "get_data", autospec=True, return_value=[{"ok": True}])

    api.entities = entities
    seen = [result async for result in api.results]

    assert len(seen) == 5
    assert all(result.success for result in seen)
    assert {tuple(r.entity.se) for r in seen} == {tuple(e.se) for e in entities}


async def test_results_partial_failure(mocker):
    entities = build_entities(4)
    failing_entity = entities[1]

    async def fake_get_data(self, payload, endpoint=None):
        if payload.se == failing_entity.se:
            raise ValueError("boom")
        return [{"se": payload.se}]

    mocker.patch.object(AsyncDuplaAccess, "get_data", autospec=True, side_effect=fake_get_data)

    api = build_dummy_async_access()
    api.entities = entities
    results = {tuple(r.entity.se): r async for r in api.results}

    assert len(results) == 4
    failing_result = results[tuple(failing_entity.se)]
    assert not failing_result.success
    assert isinstance(failing_result.error, ValueError)
    for entity in entities:
        if entity is failing_entity:
            continue
        assert results[tuple(entity.se)].success


async def test_max_concurrency_bounds_concurrent_queries(mocker):
    entities = build_entities(20)
    active = 0
    peak = 0

    async def fake_get_data(self, payload, endpoint=None):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        return []

    mocker.patch.object(AsyncDuplaAccess, "get_data", autospec=True, side_effect=fake_get_data)

    api = build_dummy_async_access(max_concurrency=4)
    api.entities = entities
    results = [result async for result in api.results]

    assert len(results) == 20
    assert peak == 4


async def test_results_is_single_shot(mocker):
    mocker.patch.object(AsyncDuplaAccess, "get_data", autospec=True, return_value=[])
    api = build_dummy_async_access()
    api.entities = build_entities(3)

    first_pass = [result async for result in api.results]
    second_pass = [result async for result in api.results]

    assert len(first_pass) == 3
    assert len(second_pass) == 0


async def test_entities_setter_resets_results(mocker):
    mocker.patch.object(AsyncDuplaAccess, "get_data", autospec=True, return_value=[])
    api = build_dummy_async_access()

    api.entities = build_entities(2)
    first_batch = [result async for result in api.results]
    assert len(first_batch) == 2

    api.entities = build_entities(3)
    second_batch = [result async for result in api.results]
    assert len(second_batch) == 3


async def test_get_data_end_to_end(mock_async_client, mocked_async_requests_long_expiration_time):
    _, mock_request = mocked_async_requests_long_expiration_time

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": [{"hello": "world"}]}

    mock_request.return_value = FakeResponse()

    api = build_dummy_async_access(max_tries=1)
    entity = build_entities(1)[0]

    async with api:
        data = await api.get_data(entity)

    assert data == [{"hello": "world"}]
