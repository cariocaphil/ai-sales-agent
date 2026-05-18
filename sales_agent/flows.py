import asyncio

from sales_agent.agents_factory import get_agents
from sales_agent.config import (
    EMAIL_GENERATED_STATUS,
    GENERATION_FAILED_STATUS,
    MISSING_INPUT_STATUS,
    NO_EMAIL_TO_SEND_STATUS,
    SEND_COMPLETE_STATUS,
    SEND_FAILED_STATUS,
)
from sales_agent.errors import (
    OutputValidationError,
    ProductContextValidationError,
    user_message,
)
from sales_agent.messages import (
    email_generation_message,
    picker_input_message,
    send_email_message,
)
from sales_agent.output_validation import validate_generation_output
from sales_agent.product_context_validation import validate_product_context
from sales_agent.runner import AgentRunner, default_runner
from sales_agent.schemas import GenerationResult


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


def generation_validation_error(message: str) -> GenerationResult:
    return GenerationResult.failure(message)


async def generate_emails(
    receiver_email,
    recipient_title,
    product_context,
    *,
    runner: AgentRunner | None = None,
):
    missing = missing_fields(
        recipient_title=recipient_title,
    )
    if missing:
        return generation_error_result(
            MISSING_INPUT_STATUS.format(fields=", ".join(missing))
        )

    try:
        validated_product_context = validate_product_context(product_context)
    except ProductContextValidationError as exc:
        return generation_validation_error(str(exc))

    agent_runner = runner or default_runner

    try:
        agents = get_agents()
        message = email_generation_message(
            recipient_title,
            validated_product_context,
        )

        results = await asyncio.gather(
            agent_runner.run(agents.professional, message),
            agent_runner.run(agents.engaging, message),
            agent_runner.run(agents.concise, message),
        )

        draft_1 = results[0].final_output
        draft_2 = results[1].final_output
        draft_3 = results[2].final_output

        picker_input = picker_input_message(draft_1, draft_2, draft_3)

        best = await agent_runner.run(agents.picker, picker_input)

        selection = best.final_output

        try:
            validated_output = validate_generation_output(
                selection.explanation,
                selection.selected_email,
            )
        except OutputValidationError as exc:
            return generation_validation_error(str(exc))

        return GenerationResult(
            draft_1=draft_1,
            draft_2=draft_2,
            draft_3=draft_3,
            explanation=validated_output.explanation,
            selected_email=validated_output.selected_email,
            status=EMAIL_GENERATED_STATUS,
            ready_to_send=True,
        )
    except Exception as exc:
        return generation_error_result(user_message(exc))


async def send_selected_email(
    receiver_email,
    selected_email,
    *,
    runner: AgentRunner | None = None,
):
    missing = missing_fields(
        receiver_email=receiver_email,
    )
    if missing:
        return MISSING_INPUT_STATUS.format(fields=", ".join(missing))

    if not selected_email or not selected_email.strip():
        return NO_EMAIL_TO_SEND_STATUS

    agent_runner = runner or default_runner

    try:
        agents = get_agents()
        message = send_email_message(receiver_email, selected_email)

        await agent_runner.run(agents.send_manager, message)

        return SEND_COMPLETE_STATUS.format(receiver=receiver_email)
    except Exception as exc:
        return SEND_FAILED_STATUS.format(error=user_message(exc))
