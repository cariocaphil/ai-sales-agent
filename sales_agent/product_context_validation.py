import re

from sales_agent.config import (
    PRODUCT_CONTEXT_INSTRUCTION_LIKE_ERROR,
    PRODUCT_CONTEXT_MAX_LENGTH,
    PRODUCT_CONTEXT_TOO_LONG_ERROR,
    PRODUCT_CONTEXT_EMPTY_ERROR,
)
from sales_agent.errors import ProductContextValidationError

_INSTRUCTION_LIKE_PATTERNS = (
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all\s+prior|previous)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\b", re.IGNORECASE),
    re.compile(r"new\s+instructions?\b", re.IGNORECASE),
    re.compile(r"system\s+prompt\b", re.IGNORECASE),
    re.compile(r"\bact\s+as\b", re.IGNORECASE),
    re.compile(r"override\s+(the\s+)?(instructions?|rules?)", re.IGNORECASE),
    re.compile(r"do\s+not\s+follow\s+(the\s+)?(above|prior|previous)", re.IGNORECASE),
    re.compile(r"instead,?\s+(write|say|respond|output)\b", re.IGNORECASE),
)


def validate_product_context(product_context: str | None) -> str:
    """
    Validate and return normalized product context.

    Raises ProductContextValidationError with a user-facing message when invalid.
    """
    if product_context is None or not str(product_context).strip():
        raise ProductContextValidationError(PRODUCT_CONTEXT_EMPTY_ERROR)

    value = str(product_context).strip()

    if len(value) > PRODUCT_CONTEXT_MAX_LENGTH:
        raise ProductContextValidationError(
            PRODUCT_CONTEXT_TOO_LONG_ERROR.format(
                max_length=PRODUCT_CONTEXT_MAX_LENGTH,
                length=len(value),
            )
        )

    for pattern in _INSTRUCTION_LIKE_PATTERNS:
        if pattern.search(value):
            raise ProductContextValidationError(PRODUCT_CONTEXT_INSTRUCTION_LIKE_ERROR)

    return value
