import re
from dataclasses import dataclass

from sales_agent.config import (
    EMAIL_OUTPUT_MAX_LENGTH,
    EMAIL_OUTPUT_MIN_LENGTH,
    EXPLANATION_OUTPUT_MAX_LENGTH,
    OUTPUT_BANNED_PHRASES,
    OUTPUT_LEAKED_PROMPT_MARKERS,
    OUTPUT_PLACEHOLDER_PATTERNS,
    OUTPUT_VALIDATION_BANNED_PHRASE_ERROR,
    OUTPUT_VALIDATION_EMAIL_LENGTH_ERROR,
    OUTPUT_VALIDATION_EMPTY_ERROR,
    OUTPUT_VALIDATION_EXPLANATION_LENGTH_ERROR,
    OUTPUT_VALIDATION_LEAKAGE_ERROR,
    OUTPUT_VALIDATION_PLACEHOLDER_ERROR,
)
from sales_agent.errors import OutputValidationError

_COMPILED_PLACEHOLDER_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE) for pattern in OUTPUT_PLACEHOLDER_PATTERNS
)


@dataclass(frozen=True)
class ValidatedGenerationOutput:
    explanation: str
    selected_email: str


def _contains_banned_phrase(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in OUTPUT_BANNED_PHRASES)


def _contains_leaked_marker(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in OUTPUT_LEAKED_PROMPT_MARKERS)


def _contains_placeholder_artifact(text: str) -> bool:
    return any(pattern.search(text) for pattern in _COMPILED_PLACEHOLDER_PATTERNS)


def validate_generation_output(
    explanation: str | None,
    selected_email: str | None,
) -> ValidatedGenerationOutput:
    """
    Validate picker output before returning results to the UI.

    Raises OutputValidationError with a user-facing message when invalid.
    """
    if explanation is None or not str(explanation).strip():
        raise OutputValidationError(OUTPUT_VALIDATION_EMPTY_ERROR)

    if selected_email is None or not str(selected_email).strip():
        raise OutputValidationError(OUTPUT_VALIDATION_EMPTY_ERROR)

    normalized_explanation = str(explanation).strip()
    normalized_email = str(selected_email).strip()

    if len(normalized_email) < EMAIL_OUTPUT_MIN_LENGTH:
        raise OutputValidationError(OUTPUT_VALIDATION_EMAIL_LENGTH_ERROR)

    if len(normalized_email) > EMAIL_OUTPUT_MAX_LENGTH:
        raise OutputValidationError(OUTPUT_VALIDATION_EMAIL_LENGTH_ERROR)

    if len(normalized_explanation) > EXPLANATION_OUTPUT_MAX_LENGTH:
        raise OutputValidationError(OUTPUT_VALIDATION_EXPLANATION_LENGTH_ERROR)

    if _contains_placeholder_artifact(normalized_email):
        raise OutputValidationError(OUTPUT_VALIDATION_PLACEHOLDER_ERROR)

    combined_text = f"{normalized_explanation}\n{normalized_email}"

    if _contains_banned_phrase(combined_text):
        raise OutputValidationError(OUTPUT_VALIDATION_BANNED_PHRASE_ERROR)

    if _contains_leaked_marker(combined_text):
        raise OutputValidationError(OUTPUT_VALIDATION_LEAKAGE_ERROR)

    return ValidatedGenerationOutput(
        explanation=normalized_explanation,
        selected_email=normalized_email,
    )
