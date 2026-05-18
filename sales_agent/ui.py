import asyncio

import gradio as gr

from sales_agent.config import (
    APP_TITLE,
    DEFAULT_PRODUCT_CONTEXT,
    DEFAULT_RECEIVER_EMAIL,
    DEFAULT_RECIPIENT_TITLE,
    DRAFT_LINES,
    EXPLANATION_LINES,
    GENERATING_STATUS,
    INPUTS_CHANGED_STATUS,
    PRODUCT_CONTEXT_LINES,
    RECEIVER_EMAIL_CHOICES,
    STATUS_LINES,
    STEP1_READY_STATUS,
)
from sales_agent.flows import generate_emails, send_selected_email
from sales_agent.schemas import GenerationResult


def _send_button_enabled(enabled: bool):
    return gr.update(interactive=enabled)


def _wrap_generation_result(result: GenerationResult):
    return (*result.to_gradio_tuple(), _send_button_enabled(result.ready_to_send))


def reset_after_input_change():
    return (
        _send_button_enabled(False),
        "",
        INPUTS_CHANGED_STATUS,
    )


def prepare_generation():
    return (
        _send_button_enabled(False),
        "",
        GENERATING_STATUS,
    )


def gradio_generate(
    receiver_email,
    recipient_title,
    product_context,
):
    result = asyncio.run(
        generate_emails(
            receiver_email=receiver_email,
            recipient_title=recipient_title,
            product_context=product_context,
        )
    )
    return _wrap_generation_result(result)


def gradio_send(
    receiver_email,
    selected_email,
):
    status = asyncio.run(
        send_selected_email(
            receiver_email=receiver_email,
            selected_email=selected_email,
        )
    )
    if status.startswith("Failed to send email:"):
        return status, _send_button_enabled(True)

    return status, _send_button_enabled(False)


def build_demo() -> gr.Blocks:
    with gr.Blocks(title=APP_TITLE) as demo:
        selected_email_state = gr.State("")

        gr.Markdown(f"# {APP_TITLE}")

        gr.Markdown(
            """
**Two-step workflow**

1. **Generate and review** — create three drafts, pick the best one, and review it.
2. **Confirm sending** — send only after you are satisfied with the selected email.
"""
        )

        gr.Markdown("## Step 1 — Generate and review")

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

        generate_button = gr.Button(
            "Generate and Select Best Email",
            variant="primary",
        )

        gr.Markdown("### Drafts")

        with gr.Row():
            draft_1_output = gr.Textbox(
                label="Professional draft",
                lines=DRAFT_LINES,
                interactive=False,
            )

            draft_2_output = gr.Textbox(
                label="Engaging draft",
                lines=DRAFT_LINES,
                interactive=False,
            )

            draft_3_output = gr.Textbox(
                label="Concise draft",
                lines=DRAFT_LINES,
                interactive=False,
            )

        gr.Markdown("### Selection")

        explanation_output = gr.Textbox(
            label="Why this email was selected",
            lines=EXPLANATION_LINES,
            interactive=False,
        )

        selected_email_output = gr.Textbox(
            label="Best selected email",
            lines=DRAFT_LINES,
            interactive=False,
        )

        gr.Markdown("## Step 2 — Confirm sending")

        send_button = gr.Button(
            "Confirm Send",
            interactive=False,
        )

        status_output = gr.Textbox(
            label="Status",
            value=STEP1_READY_STATUS,
            lines=STATUS_LINES,
            interactive=False,
        )

        generate_event = generate_button.click(
            fn=prepare_generation,
            inputs=[],
            outputs=[send_button, selected_email_state, status_output],
        )
        generate_event.then(
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
                send_button,
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
                send_button,
            ],
        )

        for input_component in (receiver_email, recipient_title, product_context):
            input_component.change(
                fn=reset_after_input_change,
                inputs=[],
                outputs=[send_button, selected_email_state, status_output],
            )

    return demo


demo = build_demo()
