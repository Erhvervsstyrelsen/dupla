import uuid

import dupla
import dupla.version
from dupla.base import DuplaApiBase


def test_token_refreshed_if_expired(mocked_requests_very_short_expiration_time, mocker):
    mock_session_post, mock_session_request = mocked_requests_very_short_expiration_time
    api = DuplaApiBase(
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        "pkcs12_filename",
        "pkcs12_password",
        "http://billetautomat.dk/url",
        5,
    )
    authentication_spy = mocker.spy(api, "_authenticate")

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
        5,
    )
    authentication_spy = mocker.spy(api, "_authenticate")

    api.get("http://some_api.dk/url")
    api.get("http://some_api.dk/url")

    authentication_spy.assert_called_once()
    mock_session_post.assert_called_once()
    assert mock_session_request.call_count == 2


def test_version_import():
    assert hasattr(dupla, "__version__")
    assert isinstance(dupla.__version__, str)
    assert dupla.__version__ == dupla.version.__version__
    assert dupla.__version__ == str(dupla.version.version_obj)
