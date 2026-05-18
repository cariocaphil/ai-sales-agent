import os

import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To
from agents import function_tool

from sales_agent.errors import ConfigurationError, EmailSendError


def _from_email() -> str | None:
    return os.environ.get("SENDGRID_FROM_EMAIL")


def _require_sendgrid_config() -> None:
    if not os.environ.get("SENDGRID_API_KEY"):
        raise ConfigurationError("SENDGRID_API_KEY is not set in the environment.")

    if not _from_email():
        raise ConfigurationError("SENDGRID_FROM_EMAIL is not set in the environment.")


def deliver_email(body: str, receiver_email: str) -> dict:
    """Send an email via SendGrid. Used by the agent tool and tests."""

    _require_sendgrid_config()

    if not receiver_email or not receiver_email.strip():
        raise EmailSendError("Receiver email is required.")

    if not body or not body.strip():
        raise EmailSendError("Email body is empty.")

    try:
        sg = sendgrid.SendGridAPIClient(
            api_key=os.environ.get("SENDGRID_API_KEY")
        )

        from_email = Email(_from_email())
        to_email = To(receiver_email)

        content = Content("text/plain", body)

        mail = Mail(
            from_email,
            to_email,
            "Sales email",
            content,
        ).get()

        response = sg.client.mail.send.post(request_body=mail)
    except (ConfigurationError, EmailSendError):
        raise
    except Exception as exc:
        raise EmailSendError(f"SendGrid request failed: {exc}") from exc

    if response.status_code >= 400:
        raise EmailSendError(
            f"SendGrid returned status {response.status_code}."
        )

    return {
        "status": "success",
        "sent_to": receiver_email,
    }


@function_tool
def send_email(body: str, receiver_email: str):
    """Send out an approved email to the receiver email."""
    return deliver_email(body, receiver_email)
