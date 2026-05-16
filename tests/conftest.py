import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from schemas import SalesPickerOutput


@pytest.fixture
def mock_run_result():
    def _factory(final_output):
        return SimpleNamespace(final_output=final_output)

    return _factory


@pytest.fixture
def sample_picker_output():
    return SalesPickerOutput(
        explanation="Clear value proposition and concise call to action.",
        selected_email="Dear Product Leader,\n\nSynthPilot can help your team.\n\nBest,\nSales",
    )


@pytest.fixture
def sample_drafts():
    return (
        "Professional draft body",
        "Engaging draft body",
        "Concise draft body",
    )


@pytest.fixture
def sendgrid_env(monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test-api-key")
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "sender@example.com")


@pytest.fixture
def mock_sendgrid_client(monkeypatch):
    mock_response = MagicMock(status_code=202)
    mock_post = MagicMock(return_value=mock_response)
    mock_send = MagicMock()
    mock_send.post = mock_post
    mock_mail = MagicMock()
    mock_mail.send = mock_send
    mock_client = MagicMock()
    mock_client.mail = mock_mail
    mock_sg = MagicMock()
    mock_sg.client = mock_client
    mock_client_class = MagicMock(return_value=mock_sg)

    monkeypatch.setattr(
        "email_service.sendgrid.SendGridAPIClient",
        mock_client_class,
    )
    return mock_client_class, mock_post


def parse_json_output(raw: str) -> SalesPickerOutput:
    return SalesPickerOutput.model_validate(json.loads(raw))
