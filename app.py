import asyncio

import gradio as gr
from agents import Runner

from agents_factory import (
    sales_agent1,
    sales_agent2,
    sales_agent3,
    sales_picker,
    send_manager,
)
from config import (
    APP_TITLE,
    DEFAULT_PRODUCT_CONTEXT,
    DEFAULT_RECEIVER_EMAIL,
    DEFAULT_RECIPIENT_TITLE,
    DRAFT_LINES,
    EMAIL_GENERATED_STATUS,
    EXPLANATION_LINES,
    NO_EMAIL_TO_SEND_STATUS,
    PRODUCT_CONTEXT_LINES,
    RECEIVER_EMAIL_CHOICES,
    STATUS_LINES,
)
from messages import (
    email_generation_message,
    picker_input_message,
    send_email_message,
)


# -----------------------------
# Generation flow
# -----------------------------

async def generate_emails(
    receiver_email,
    recipient_title,
    product_context,
):
    message = email_generation_message(recipient_title, product_context)

    results = await asyncio.gather(
        Runner.run(sales_agent1, message),
        Runner.run(sales_agent2, message),
        Runner.run(sales_agent3, message),
    )

    draft_1 = results[0].final_output
    draft_2 = results[1].final_output
    draft_3 = results[2].final_output

    picker_input = picker_input_message(draft_1, draft_2, draft_3)

    best = await Runner.run(sales_picker, picker_input)

    selection = best.final_output
    explanation = selection.explanation
    selected_email = selection.selected_email

    status = EMAIL_GENERATED_STATUS

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
        return NO_EMAIL_TO_SEND_STATUS

    message = send_email_message(receiver_email, selected_email)

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

with gr.Blocks(title=APP_TITLE) as demo:
    selected_email_state = gr.State("")

    gr.Markdown(f"# {APP_TITLE}")

    gr.Markdown(
        """
Generate three cold email drafts, let an AI picker choose the strongest one,
review the result, and then manually confirm sending.
"""
    )

    with gr.Row():
        receiver_email = gr.Dropdown(
            label="Receiver email",
            choices=RECEIVER_EMAIL_CHOICES,
            value=DEFAULT_RECEIVER_EMAIL,
            interactive=True,
        )

        recipient_title = gr.Textbox(
            label="Recipient / greeting",
            value=DEFAULT_RECIPIENT_TITLE,
        )

    product_context = gr.Textbox(
        label="Product context",
        value=DEFAULT_PRODUCT_CONTEXT,
        lines=PRODUCT_CONTEXT_LINES,
    )

    generate_button = gr.Button("Generate and Select Best Email")

    gr.Markdown("## Drafts")

    with gr.Row():
        draft_1_output = gr.Textbox(
            label="Professional draft",
            lines=DRAFT_LINES,
        )

        draft_2_output = gr.Textbox(
            label="Engaging draft",
            lines=DRAFT_LINES,
        )

        draft_3_output = gr.Textbox(
            label="Concise draft",
            lines=DRAFT_LINES,
        )

    gr.Markdown("## Selection Analysis")

    explanation_output = gr.Textbox(
        label="Why this email was selected",
        lines=EXPLANATION_LINES,
    )

    selected_email_output = gr.Textbox(
        label="Best selected email",
        lines=DRAFT_LINES,
    )

    send_button = gr.Button("Send Selected Email")

    status_output = gr.Textbox(
        label="Status",
        lines=STATUS_LINES,
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