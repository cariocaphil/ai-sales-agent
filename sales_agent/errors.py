from agents.exceptions import AgentsException, ModelBehaviorError
from pydantic import ValidationError


class AppError(Exception):
    """Error with a message safe to show in the Gradio UI."""


class ConfigurationError(AppError):
    pass


class EmailSendError(AppError):
    pass


class ProductContextValidationError(AppError):
    pass


class OutputValidationError(AppError):
    pass


def user_message(exc: BaseException) -> str:
    if isinstance(exc, AppError):
        return str(exc)

    if isinstance(exc, (ModelBehaviorError, ValidationError)):
        return (
            "The model returned an invalid response. "
            "Please try generating again."
        )

    if isinstance(exc, AgentsException):
        return f"Agent error: {exc}"

    return f"Unexpected error: {exc}"
