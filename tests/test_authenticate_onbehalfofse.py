import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from dupla.endpoint import DuplaAccess

@pytest.fixture
def client_with_onbehalfofse():
    return DuplaAccess(
        transaction_id=str(uuid4()),
        agreement_id="dummy-agreement",
        pkcs12_filename="dummy.p12",
        pkcs12_password="dummy",
        billetautomat_url="https://fake-url.com",
        onbehalfofse="987654321",  # optional
    )

@pytest.fixture
def client_without_onbehalfofse():
    return DuplaAccess(
        transaction_id=str(uuid4()),
        agreement_id="dummy-agreement",
        pkcs12_filename="dummy.p12",
        pkcs12_password="dummy",
        billetautomat_url="https://fake-url.com",
    )

@patch("dupla.base.requests.Session")
def test_authenticate_includes_onbehalfofse(mock_session, client_with_onbehalfofse):
    mock_result = MagicMock()
    mock_result.ok = True
    mock_result.json.return_value = {"access_token": "token123", "expires_in": 3600}

    mock_session.return_value.__enter__.return_value.post.return_value = mock_result

    client_with_onbehalfofse._authenticate()

    _, kwargs = mock_session.return_value.__enter__.return_value.post.call_args
    assert kwargs["data"]["onbehalfofse"] == "987654321"

@patch("dupla.base.requests.Session")
def test_authenticate_works_without_onbehalfofse(mock_session, client_without_onbehalfofse):
    mock_result = MagicMock()
    mock_result.ok = True
    mock_result.json.return_value = {"access_token": "token456", "expires_in": 3600}

    mock_session.return_value.__enter__.return_value.post.return_value = mock_result

    client_without_onbehalfofse._authenticate()

    _, kwargs = mock_session.return_value.__enter__.return_value.post.call_args
    assert "onbehalfofse" not in kwargs["data"]
