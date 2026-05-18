from unittest.mock import MagicMock

import pytest

from sales_agent.email_service import _from_email, _require_sendgrid_config, deliver_email
from sales_agent.errors import ConfigurationError, EmailSendError


def test_require_sendgrid_config_missing_api_key(monkeypatch):
    monkeypatch.delenv("SENDGRID_API_KEY", raising=False)
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "sender@example.com")

    with pytest.raises(ConfigurationError, match="SENDGRID_API_KEY"):
        _require_sendgrid_config()


def test_require_sendgrid_config_missing_from_email(monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test-key")
    monkeypatch.delenv("SENDGRID_FROM_EMAIL", raising=False)

    with pytest.raises(ConfigurationError, match="SENDGRID_FROM_EMAIL"):
        _require_sendgrid_config()


def test_from_email_reads_environment_at_call_time(monkeypatch):
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "runtime@example.com")

    assert _from_email() == "runtime@example.com"


def test_deliver_email_success(sendgrid_env, mock_sendgrid_client):
    _mock_sg, mock_post = mock_sendgrid_client

    result = deliver_email(
        body="Approved email body",
        receiver_email="recipient@example.com",
    )

    assert result == {
        "status": "success",
        "sent_to": "recipient@example.com",
    }
    mock_post.assert_called_once()


def test_deliver_email_rejects_empty_receiver(sendgrid_env):
    with pytest.raises(EmailSendError, match="Receiver email is required"):
        deliver_email(body="Hello", receiver_email="  ")


def test_deliver_email_rejects_empty_body(sendgrid_env):
    with pytest.raises(EmailSendError, match="Email body is empty"):
        deliver_email(body="", receiver_email="recipient@example.com")


def test_deliver_email_raises_on_sendgrid_http_error(sendgrid_env, monkeypatch):
    mock_response = MagicMock(status_code=500)
    mock_post = MagicMock(return_value=mock_response)
    mock_client = MagicMock()
    mock_client.mail.send.post = mock_post
    mock_sg = MagicMock()
    mock_sg.client = mock_client
    monkeypatch.setattr(
        "sales_agent.email_service.sendgrid.SendGridAPIClient",
        MagicMock(return_value=mock_sg),
    )

    with pytest.raises(EmailSendError, match="status 500"):
        deliver_email(body="Hello", receiver_email="recipient@example.com")


def test_deliver_email_wraps_unexpected_sendgrid_errors(sendgrid_env, monkeypatch):
    monkeypatch.setattr(
        "sales_agent.email_service.sendgrid.SendGridAPIClient",
        MagicMock(side_effect=RuntimeError("network down")),
    )

    with pytest.raises(EmailSendError, match="SendGrid request failed"):
        deliver_email(body="Hello", receiver_email="recipient@example.com")
