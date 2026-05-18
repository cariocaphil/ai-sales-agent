import asyncio

from agents import Runner

from agents_factory import (
    sales_agent1,
    sales_agent2,
    sales_agent3,
    sales_picker,
    send_manager,
)
from config import (
    EMAIL_GENERATED_STATUS,
    GENERATION_FAILED_STATUS,
    MISSING_INPUT_STATUS,
    NO_EMAIL_TO_SEND_STATUS,
    SEND_COMPLETE_STATUS,
    SEND_FAILED_STATUS,
)
from errors import user_message
from messages import (
    email_generation_message,
    picker_input_message,
    send_email_message,
)
from schemas import GenerationResult


def missing_fields(**fields: str | None) -> list[str]:
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


def generation_error_result(error: str) -> GenerationResult:
    return GenerationResult.failure(
        GENERATION_FAILED_STATUS.format(error=error)
    )


async def generate_emails(
    receiver_email,
    recipient_title,
    product_context,
):
    missing = missing_fields(
        recipient_title=recipient_title,
        product_context=product_context,
    )
    if missing:
        return generation_error_result(
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
            return generation_error_result(
                "The picker returned an incomplete selection."
            )

        return GenerationResult(
            draft_1=draft_1,
            draft_2=draft_2,
            draft_3=draft_3,
            explanation=explanation,
            selected_email=selected_email,
            status=EMAIL_GENERATED_STATUS,
            ready_to_send=True,
        )
    except Exception as exc:
        return generation_error_result(user_message(exc))


async def send_selected_email(
    receiver_email,
    selected_email,
):
    missing = missing_fields(
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
