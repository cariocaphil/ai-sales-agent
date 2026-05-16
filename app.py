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
    GENERATING_STATUS,
    GENERATION_FAILED_STATUS,
    INPUTS_CHANGED_STATUS,
    MISSING_INPUT_STATUS,
    NO_EMAIL_TO_SEND_STATUS,
    PRODUCT_CONTEXT_LINES,
    RECEIVER_EMAIL_CHOICES,
    SEND_COMPLETE_STATUS,
    SEND_FAILED_STATUS,
    STATUS_LINES,
    STEP1_READY_STATUS,
)
from errors import user_message
from messages import (
    email_generation_message,
    picker_input_message,
    send_email_message,
)


def _missing_fields(**fields: str | None) -> list[str]:
    labels = {
        "recipient_title": "recipient / greeting",
        "product_context": "product context",
        "receiver_email": "receiver email",
    }
    return [
        labels[name]
        for name, value in fields.items()
        if not value or not str(value).strip()
    ]


def _send_button_enabled(enabled: bool):
    return gr.update(interactive=enabled)


def _generation_error_result(error: str):
    status = GENERATION_FAILED_STATUS.format(error=error)
    return (
        "",
        "",
        "",
        "",
        "",
        "",
        status,
        _send_button_enabled(False),
    )


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


# -----------------------------
# Generation flow
# -----------------------------

async def generate_emails(
    receiver_email,
    recipient_title,
    product_context,
):
    missing = _missing_fields(
        recipient_title=recipient_title,
        product_context=product_context,
    )
    if missing:
        return _generation_error_result(
            MISSING_INPUT_STATUS.format(fields=", ".join(missing))
        )

    try:
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
        explanation = selection.explanation.strip()
        selected_email = selection.selected_email.strip()

        if not explanation or not selected_email:
            return _generation_error_result(
                "The picker returned an incomplete selection."
            )

        status = EMAIL_GENERATED_STATUS

        return (
            draft_1,
            draft_2,
            draft_3,
            explanation,
            selected_email,
            selected_email,
            status,
            _send_button_enabled(True),
        )
    except Exception as exc:
        return _generation_error_result(user_message(exc))


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
    missing = _missing_fields(
        receiver_email=receiver_email,
    )
    if missing:
        return MISSING_INPUT_STATUS.format(fields=", ".join(missing))

    if not selected_email or not selected_email.strip():
        return NO_EMAIL_TO_SEND_STATUS

    try:
        message = send_email_message(receiver_email, selected_email)

        await Runner.run(send_manager, message)

        return SEND_COMPLETE_STATUS.format(receiver=receiver_email)
    except Exception as exc:
        return SEND_FAILED_STATUS.format(error=user_message(exc))


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


# -----------------------------
# Gradio UI
# -----------------------------

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


if __name__ == "__main__":
    demo.launch()