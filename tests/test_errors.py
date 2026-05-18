import pytest
from agents.exceptions import AgentsException, ModelBehaviorError
from pydantic import ValidationError

from sales_agent.errors import ConfigurationError, user_message
from sales_agent.schemas import SalesPickerOutput


def test_user_message_returns_app_error_text():
    assert user_message(ConfigurationError("missing key")) == "missing key"


def test_user_message_handles_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        SalesPickerOutput.model_validate({"explanation": "only"})

    message = user_message(exc_info.value)

    assert "invalid response" in message


def test_user_message_handles_model_behavior_error():
    message = user_message(ModelBehaviorError("bad json"))
    assert "invalid response" in message


def test_user_message_handles_agents_exception():
    class CustomAgentsError(AgentsException):
        pass

    message = user_message(CustomAgentsError("tool failed"))
    assert message == "Agent error: tool failed"


def test_user_message_handles_generic_exception():
    assert user_message(RuntimeError("boom")) == "Unexpected error: boom"
