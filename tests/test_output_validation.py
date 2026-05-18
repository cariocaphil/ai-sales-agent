import pytest

from sales_agent.config import (
    EMAIL_OUTPUT_MAX_LENGTH,
    EMAIL_OUTPUT_MIN_LENGTH,
    OUTPUT_VALIDATION_BANNED_PHRASE_ERROR,
    OUTPUT_VALIDATION_EMPTY_ERROR,
    OUTPUT_VALIDATION_LEAKAGE_ERROR,
    OUTPUT_VALIDATION_PLACEHOLDER_ERROR,
)
from sales_agent.errors import OutputValidationError
from sales_agent.output_validation import validate_generation_output


def _valid_email(length: int | None = None) -> str:
    body = (
        "Dear Product Leader,\n\n"
        "We help teams turn feedback into clear product priorities. "
        "Would you be open to a short conversation next week?\n\n"
        "Best regards,\nSales"
    )
    if length is None:
        return body
    if len(body) >= length:
        return body[:length]
    return body + ("x" * (length - len(body)))


def test_validate_generation_output_accepts_valid_output():
    result = validate_generation_output(
        explanation="Clear value proposition and respectful tone.",
        selected_email=_valid_email(),
    )

    assert result.explanation == "Clear value proposition and respectful tone."
    assert "Dear Product Leader" in result.selected_email


def test_validate_generation_output_rejects_empty_explanation():
    with pytest.raises(OutputValidationError, match="missing"):
        validate_generation_output(
            explanation="   ",
            selected_email=_valid_email(),
        )


def test_validate_generation_output_rejects_empty_email():
    with pytest.raises(OutputValidationError, match="missing"):
        validate_generation_output(
            explanation="A solid draft.",
            selected_email="",
        )


def test_validate_generation_output_rejects_email_that_is_too_short():
    with pytest.raises(OutputValidationError, match="length"):
        validate_generation_output(
            explanation="Too short.",
            selected_email="Hi there",
        )


def test_validate_generation_output_rejects_email_that_is_too_long():
    base_email = _valid_email()
    too_long_email = base_email + ("x" * (EMAIL_OUTPUT_MAX_LENGTH - len(base_email) + 1))

    with pytest.raises(OutputValidationError, match="length"):
        validate_generation_output(
            explanation="Too long.",
            selected_email=too_long_email,
        )


def test_validate_generation_output_rejects_unresolved_placeholders():
    with pytest.raises(OutputValidationError) as exc_info:
        validate_generation_output(
            explanation="Looks fine.",
            selected_email=_valid_email().replace(
                "Dear Product Leader",
                "Hello {product_context}",
            ),
        )

    assert str(exc_info.value) == OUTPUT_VALIDATION_PLACEHOLDER_ERROR


def test_validate_generation_output_rejects_banned_phrases():
    with pytest.raises(OutputValidationError) as exc_info:
        validate_generation_output(
            explanation="Strong CTA.",
            selected_email=_valid_email().replace(
                "product priorities",
                "guaranteed results for every team",
            ),
        )

    assert str(exc_info.value) == OUTPUT_VALIDATION_BANNED_PHRASE_ERROR


def test_validate_generation_output_rejects_prompt_leakage_markers():
    with pytest.raises(OutputValidationError) as exc_info:
        validate_generation_output(
            explanation="Mentions the system prompt in the draft.",
            selected_email=_valid_email(),
        )

    assert str(exc_info.value) == OUTPUT_VALIDATION_LEAKAGE_ERROR


def test_validate_generation_output_rejects_as_an_ai_phrase():
    email = _valid_email()
    email = email.replace("Sales", "As an AI assistant, I recommend a call.")

    with pytest.raises(OutputValidationError, match="not allowed"):
        validate_generation_output(
            explanation="Polite tone.",
            selected_email=email,
        )


def test_validate_generation_output_accepts_email_at_min_length_boundary():
    email = "a" * EMAIL_OUTPUT_MIN_LENGTH

    result = validate_generation_output(
        explanation="Boundary check.",
        selected_email=email,
    )

    assert len(result.selected_email) == EMAIL_OUTPUT_MIN_LENGTH
