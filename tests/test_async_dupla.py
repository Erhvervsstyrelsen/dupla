import asyncio
import uuid

import pytest

from dupla.async_base import AsyncDuplaApiBase
from dupla.exceptions import DuplaApiUsageException


def build_dummy_async_api(jwt_token_expiration_overlap: int = 5, **kwargs) -> AsyncDuplaApiBase:
    return AsyncDuplaApiBase(
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        "pkcs12_filename",
        "pkcs12_password",
        "http://billetautomat.dk/url",
        jwt_token_expiration_overlap,
        **kwargs,
    )


async def test_token_refreshed_if_expired(
    mock_async_client, mocked_async_requests_very_short_expiration_time, mocker
):
    mock_post, mock_request = mocked_async_requests_very_short_expiration_time
    api = build_dummy_async_api()
    authentication_spy = mocker.spy(api, "_authenticate")

    async with api:
        await api.get("http://some_api.dk/url")
        await api.get("http://some_api.dk/url")

    assert authentication_spy.call_count == 2
    assert mock_post.call_count == 2
    assert mock_request.call_count == 2


async def test_token_not_refreshed_if_not_expired(
    mock_async_client, mocked_async_requests_long_expiration_time, mocker
):
    mock_post, mock_request = mocked_async_requests_long_expiration_time
    api = build_dummy_async_api()
    authentication_spy = mocker.spy(api, "_authenticate")

    async with api:
        await api.get("http://some_api.dk/url")
        await api.get("http://some_api.dk/url")

    authentication_spy.assert_called_once()
    mock_post.assert_called_once()
    assert mock_request.call_count == 2


async def test_concurrent_requests_share_single_authentication(
    mock_async_client, mocked_async_requests_long_expiration_time, mocker
):
    """Several concurrent callers racing on a missing token should trigger only one
    `_authenticate` call - the rest should reuse the token it fetched."""
    mock_post, mock_request = mocked_async_requests_long_expiration_time
    api = build_dummy_async_api()
    authentication_spy = mocker.spy(api, "_authenticate")

    async with api:
        await asyncio.gather(*(api.get("http://some_api.dk/url") for _ in range(10)))

    authentication_spy.assert_called_once()
    mock_post.assert_called_once()
    assert mock_request.call_count == 10


async def test_request_outside_context_manager_raises():
    api = build_dummy_async_api()
    with pytest.raises(DuplaApiUsageException):
        await api.get("http://some_api.dk/url")
