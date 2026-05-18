from sales_agent.prompts import EMAIL_GENERATION_MESSAGE_TEMPLATE


def email_generation_message(recipient_title: str, product_context: str) -> str:
    return EMAIL_GENERATION_MESSAGE_TEMPLATE.format(
        recipient_title=recipient_title,
        product_context=product_context,
    ).strip()


def picker_input_message(draft_1: str, draft_2: str, draft_3: str) -> str:
    return f"""
Cold sales emails:

Email 1:
{draft_1}

Email 2:
{draft_2}

Email 3:
{draft_3}
"""


def send_email_message(receiver_email: str, selected_email: str) -> str:
    return f"""
Send this approved email exactly as written.

Receiver email:
{receiver_email}

Approved email:
{selected_email}
"""
