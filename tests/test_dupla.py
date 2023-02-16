import uuid
import pytest
import requests
import requests_pkcs12

from dupla.dupla import DuplaApiBase


class Object:
    pass


def get_jwt_token_response(expiration_time: int):
    response = Object()
    response.status_code = 200
    response.ok = True
    response.json = lambda: {
        "access_token": str(uuid.uuid4()),
        "expires_in": expiration_time
    }
    return response


def get_mocked_requests_for_expiration(mocker, expiration_time):
    session_object = requests.Session()
    mock_session_post = mocker.patch.object(session_object, 'post', autospec=True)
    mock_session_post.return_value = get_jwt_token_response(expiration_time)

    mock_session_request = mocker.patch.object(session_object, 'request', autospec=True)
    mock_session_request.return_value = Object()

    mocker.patch.object(session_object, "mount", autospec=True)

    mock_pkcs = mocker.patch.object(requests_pkcs12, "Pkcs12Adapter", autospec=True)
    mock_pkcs.return_value = Object()

    mock_session = mocker.patch.object(requests, 'Session', autospec=True)
    mock_session.return_value = session_object

    return mock_session_post, mock_session_request


@pytest.fixture
def mocked_requests_very_short_expiration_time(mocker):
    return get_mocked_requests_for_expiration(mocker, expiration_time=2)


@pytest.fixture
def mocked_requests_long_expiration_time(mocker):
    return get_mocked_requests_for_expiration(mocker, expiration_time=180)


def test_token_refreshed_if_expired(mocked_requests_very_short_expiration_time, mocker):
    mock_session_post, mock_session_request = mocked_requests_very_short_expiration_time
    api = DuplaApiBase(
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        "pkcs12_filename",
        "pkcs12_password",
        "http://billetautomat.dk/url",
        5
    )
    authentication_spy = mocker.spy(api, '_authenticate')

    api.get("http://some_api.dk/url")
    api.get("http://some_api.dk/url")

    assert authentication_spy.call_count == 2
    assert mock_session_post.call_count == 2
    assert mock_session_request.call_count == 2


def test_token_not_refreshed_if_not_expired(mocked_requests_long_expiration_time, mocker):
    mock_session_post, mock_session_request = mocked_requests_long_expiration_time
    api = DuplaApiBase(
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        "pkcs12_filename",
        "pkcs12_password",
        "http://billetautomat.dk/url",
        5
    )
    authentication_spy = mocker.spy(api, '_authenticate')

    api.get("http://some_api.dk/url")
    api.get("http://some_api.dk/url")

    authentication_spy.assert_called_once()
    mock_session_post.assert_called_once()
    assert mock_session_request.call_count == 2