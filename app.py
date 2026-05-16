import os
import asyncio
import gradio as gr
import sendgrid

from dotenv import load_dotenv
from sendgrid.helpers.mail import Mail, Email, To, Content
from agents import Agent, Runner, function_tool

load_dotenv()

FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")


# -----------------------------
# Sales agents
# -----------------------------

instructions1 = """
You are a professional sales agent working for SynthPilot,
a fictional AI product that helps software teams automatically analyze user feedback,
detect product pain points, and generate prioritized feature recommendations.

You write professional, serious cold emails.
"""

instructions2 = """
You are a humorous, engaging sales agent working for SynthPilot,
a fictional AI product that helps software teams automatically analyze user feedback,
detect product pain points, and generate prioritized feature recommendations.

You write witty, engaging cold emails that are likely to get a response.
"""

instructions3 = """
You are a busy sales agent working for SynthPilot,
a fictional AI product that helps software teams automatically analyze user feedback,
detect product pain points, and generate prioritized feature recommendations.

You write concise, to-the-point cold emails.
"""


sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=instructions1,
    model="gpt-4o-mini",
)

sales_agent2 = Agent(
    name="Engaging Sales Agent",
    instructions=instructions2,
    model="gpt-4o-mini",
)

sales_agent3 = Agent(
    name="Busy Sales Agent",
    instructions=instructions3,
    model="gpt-4o-mini",
)

sales_picker = Agent(
    name="Sales Picker",
    instructions="""
You pick the best cold sales email from the given options.

Imagine you are the customer and pick the one you would be most likely to respond to.

Return your answer EXACTLY in this format:

EXPLANATION:
<short explanation>

SELECTED_EMAIL:
<full selected email>
""",
    model="gpt-4o-mini",
)


# -----------------------------
# Send email tool
# -----------------------------

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
    instructions="""
You are responsible only for sending an already approved sales email.

Rules:
- Do not rewrite the email.
- Do not improve the email.
- Do not generate a new email.
- Send exactly the approved email provided to you.
- Use the send_email tool.
""",
    tools=[send_email],
    model="gpt-4o-mini",
)


# -----------------------------
# Generation flow
# -----------------------------

async def generate_emails(
    receiver_email,
    recipient_title,
    product_context,
):
    message = f"""
Write a cold sales email addressed to: {recipient_title}

Product context:
{product_context}
"""

    results = await asyncio.gather(
        Runner.run(sales_agent1, message),
        Runner.run(sales_agent2, message),
        Runner.run(sales_agent3, message),
    )

    draft_1 = results[0].final_output
    draft_2 = results[1].final_output
    draft_3 = results[2].final_output

    picker_input = f"""
Cold sales emails:

Email 1:
{draft_1}

Email 2:
{draft_2}

Email 3:
{draft_3}
"""

    best = await Runner.run(sales_picker, picker_input)

    selected_response = best.final_output
    parts = selected_response.split("SELECTED_EMAIL:")

    explanation = parts[0].replace("EXPLANATION:", "").strip()
    selected_email = parts[1].strip()

    status = "Email generated and selected. Review it, then click Send Selected Email."

    return (
        draft_1,
        draft_2,
        draft_3,
        explanation,
        selected_email,
        selected_email,
        status,
    )


def gradio_generate(
    receiver_email,
    recipient_title,
    product_context,
):
    return asyncio.run(
        generate_emails(
            receiver_email=receiver_email,
            recipient_title=recipient_title,
            product_context=product_context,
        )
    )


# -----------------------------
# Sending flow
# -----------------------------

async def send_selected_email(
    receiver_email,
    selected_email,
):
    if not selected_email or not selected_email.strip():
        return "No selected email to send yet. Generate emails first."

    message = f"""
Send this approved email exactly as written.

Receiver email:
{receiver_email}

Approved email:
{selected_email}
"""

    await Runner.run(send_manager, message)

    return f"Email sent to {receiver_email}"


def gradio_send(
    receiver_email,
    selected_email,
):
    return asyncio.run(
        send_selected_email(
            receiver_email=receiver_email,
            selected_email=selected_email,
        )
    )


# -----------------------------
# Gradio UI
# -----------------------------

with gr.Blocks(title="AI Sales Agent") as demo:
    selected_email_state = gr.State("")

    gr.Markdown("# AI Sales Agent")

    gr.Markdown(
        """
Generate three cold email drafts, let an AI picker choose the strongest one,
review the result, and then manually confirm sending.
"""
    )

    with gr.Row():
        receiver_email = gr.Dropdown(
            label="Receiver email",
            choices=["cariocaphil@gmail.com"],
            value="cariocaphil@gmail.com",
            interactive=True,
        )

        recipient_title = gr.Textbox(
            label="Recipient / greeting",
            value="Dear Product Leader",
        )

    product_context = gr.Textbox(
        label="Product context",
        value=(
            "SynthPilot helps software teams analyze user feedback, "
            "detect product pain points, and generate prioritized "
            "feature recommendations."
        ),
        lines=4,
    )

    generate_button = gr.Button("Generate and Select Best Email")

    gr.Markdown("## Drafts")

    with gr.Row():
        draft_1_output = gr.Textbox(
            label="Professional draft",
            lines=14,
        )

        draft_2_output = gr.Textbox(
            label="Engaging draft",
            lines=14,
        )

        draft_3_output = gr.Textbox(
            label="Concise draft",
            lines=14,
        )

    gr.Markdown("## Selection Analysis")

    explanation_output = gr.Textbox(
        label="Why this email was selected",
        lines=4,
    )

    selected_email_output = gr.Textbox(
        label="Best selected email",
        lines=14,
    )

    send_button = gr.Button("Send Selected Email")

    status_output = gr.Textbox(
        label="Status",
        lines=2,
    )

    generate_button.click(
        fn=gradio_generate,
        inputs=[
            receiver_email,
            recipient_title,
            product_context,
        ],
        outputs=[
            draft_1_output,
            draft_2_output,
            draft_3_output,
            explanation_output,
            selected_email_output,
            selected_email_state,
            status_output,
        ],
    )

    send_button.click(
        fn=gradio_send,
        inputs=[
            receiver_email,
            selected_email_state,
        ],
        outputs=[
            status_output,
        ],
    )


if __name__ == "__main__":
    demo.launch()