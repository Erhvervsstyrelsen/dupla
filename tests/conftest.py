import uuid

import httpx
import httpx_pkcs12
import pytest

from dupla.endpoint import DuplaAccess


class Object:
    pass


def get_jwt_token_response(expiration_time: int):
    response = Object()
    response.status_code = 200
    response.is_success = True
    response.json = lambda: {
        "access_token": str(uuid.uuid4()),
        "expires_in": expiration_time,
    }
    return response


@pytest.fixture
def session_object():
    return httpx.Client()


@pytest.fixture
def mock_session(mocker, session_object):
    # The mocked httpx.Client() call always returns the same `session_object`, so its
    # open/closed state tracking must be disabled to allow entering it as a context
    # manager across multiple calls.
    mocker.patch.object(httpx.Client, "__enter__", lambda self: self)
    mocker.patch.object(httpx.Client, "__exit__", lambda self, *args: None)
    mock_session = mocker.patch.object(httpx, "Client", autospec=True)
    mock_session.return_value = session_object
    return mock_session


@pytest.fixture
def mock_session_post(mocker, session_object):
    mock_session_post = mocker.patch.object(session_object, "post", autospec=True)
    mock_session_post.return_value = get_jwt_token_response(10)
    return mock_session_post


@pytest.fixture
def mock_session_request(mocker, session_object):
    mock_request = mocker.patch.object(session_object, "request", autospec=True)
    mock_request.return_value = Object()
    return mock_request


@pytest.fixture
def mock_session_pkcs(mocker):
    mock_pkcs = mocker.patch.object(httpx_pkcs12, "create_ssl_context", autospec=True)
    mock_pkcs.return_value = Object()
    return mock_pkcs


@pytest.fixture
def get_mocked_requests_for_expiration(mock_session_post, mock_session_request):
    def _getter(expiration_time):
        mock_session_post.return_value = get_jwt_token_response(expiration_time)
        return mock_session_post, mock_session_request

    return _getter


@pytest.fixture(autouse=True)
def mock_run_payload(mocker):
    mock_runner = mocker.patch.object(DuplaAccess, "_run_payload", autospec=True)
    return mock_runner


@pytest.fixture(autouse=True)
def default_mock_requests(
    mocker,
    session_object,
    mock_session,
    mock_session_post,
    mock_session_request,
    mock_session_pkcs,
):
    """Ensure requests and pkcs is mocked by default.
    Prevents accidentally sending out requests by the API's."""


@pytest.fixture
def mocked_requests_very_short_expiration_time(get_mocked_requests_for_expiration):
    return get_mocked_requests_for_expiration(expiration_time=2)


@pytest.fixture
def mocked_requests_long_expiration_time(get_mocked_requests_for_expiration):
    return get_mocked_requests_for_expiration(expiration_time=180)
