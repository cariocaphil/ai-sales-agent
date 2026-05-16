import os

import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import Content, Email, Mail, To
from agents import function_tool

from errors import ConfigurationError, EmailSendError

load_dotenv()

FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")


def _require_sendgrid_config() -> None:
    if not os.environ.get("SENDGRID_API_KEY"):
        raise ConfigurationError("SENDGRID_API_KEY is not set in the environment.")

    if not FROM_EMAIL:
        raise ConfigurationError("SENDGRID_FROM_EMAIL is not set in the environment.")


@function_tool
def send_email(body: str, receiver_email: str):
    """Send out an approved email to the receiver email."""

    _require_sendgrid_config()

    if not receiver_email or not receiver_email.strip():
        raise EmailSendError("Receiver email is required.")

    if not body or not body.strip():
        raise EmailSendError("Email body is empty.")

    try:
        sg = sendgrid.SendGridAPIClient(
            api_key=os.environ.get("SENDGRID_API_KEY")
        )

        from_email = Email(FROM_EMAIL)
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
