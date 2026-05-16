import os

import sendgrid
from dotenv import load_dotenv
from sendgrid.helpers.mail import Content, Email, Mail, To
from agents import Agent, function_tool

from prompts import SEND_MANAGER_INSTRUCTIONS

load_dotenv()

FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")


@function_tool
def send_email(body: str, receiver_email: str):
    """Send out an approved email to the receiver email."""

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

    sg.client.mail.send.post(request_body=mail)

    return {
        "status": "success",
        "sent_to": receiver_email,
    }


send_manager = Agent(
    name="Send Manager",
    instructions=SEND_MANAGER_INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
