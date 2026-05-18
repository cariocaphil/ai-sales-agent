import pytest
from unittest.mock import AsyncMock

from sales_agent.config import (
    MISSING_INPUT_STATUS,
    NO_EMAIL_TO_SEND_STATUS,
    SEND_COMPLETE_STATUS,
    SEND_FAILED_STATUS,
)
from sales_agent.errors import EmailSendError
from sales_agent.flows import missing_fields, send_selected_email
from tests.conftest import FakeAgentRunner


def test_missing_fields_detects_blank_receiver():
    assert missing_fields(receiver_email="  ") == ["receiver email"]


@pytest.mark.asyncio
async def test_send_selected_email_requires_receiver():
    status = await send_selected_email(
        receiver_email="",
        selected_email="Hello",
    )

    assert status == MISSING_INPUT_STATUS.format(fields="receiver email")


@pytest.mark.asyncio
async def test_send_selected_email_requires_selected_email():
    status = await send_selected_email(
        receiver_email="user@example.com",
        selected_email="",
    )

    assert status == NO_EMAIL_TO_SEND_STATUS


@pytest.mark.asyncio
async def test_send_selected_email_success():
    mock_run = AsyncMock()
    status = await send_selected_email(
        receiver_email="user@example.com",
        selected_email="Approved body",
        runner=FakeAgentRunner(mock_run),
    )

    assert status == SEND_COMPLETE_STATUS.format(receiver="user@example.com")
    mock_run.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_selected_email_returns_failure_message():
    async def failing_run(agent, message):
        raise EmailSendError("SendGrid returned status 500.")

    status = await send_selected_email(
        receiver_email="user@example.com",
        selected_email="Approved body",
        runner=FakeAgentRunner(failing_run),
    )

    assert status == SEND_FAILED_STATUS.format(
        error="SendGrid returned status 500."
    )
