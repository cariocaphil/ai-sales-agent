import asyncio

import gradio as gr
from dotenv import load_dotenv
from agents import Agent, Runner

from email_service import send_manager
from messages import (
    email_generation_message,
    picker_input_message,
    send_email_message,
)
from prompts import (
    CONCISE_SALES_INSTRUCTIONS,
    ENGAGING_SALES_INSTRUCTIONS,
    PROFESSIONAL_SALES_INSTRUCTIONS,
    SALES_PICKER_INSTRUCTIONS,
)

load_dotenv()


# -----------------------------
# Sales agents
# -----------------------------

sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=PROFESSIONAL_SALES_INSTRUCTIONS,
    model="gpt-4o-mini",
)

sales_agent2 = Agent(
    name="Engaging Sales Agent",
    instructions=ENGAGING_SALES_INSTRUCTIONS,
    model="gpt-4o-mini",
)

sales_agent3 = Agent(
    name="Busy Sales Agent",
    instructions=CONCISE_SALES_INSTRUCTIONS,
    model="gpt-4o-mini",
)

sales_picker = Agent(
    name="Sales Picker",
    instructions=SALES_PICKER_INSTRUCTIONS,
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