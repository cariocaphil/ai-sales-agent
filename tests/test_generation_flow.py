import pytest
from unittest.mock import AsyncMock, patch

from config import (
    EMAIL_GENERATED_STATUS,
    GENERATION_FAILED_STATUS,
    MISSING_INPUT_STATUS,
)
from flows import generate_emails, generation_error_result, missing_fields
from schemas import GenerationResult, SalesPickerOutput


def test_missing_fields_detects_blank_product_context():
    assert missing_fields(
        recipient_title="Dear Leader",
        product_context="",
    ) == ["product context"]


def test_generation_error_result_shape():
    result = generation_error_result("something went wrong")

    assert result == GenerationResult.failure(
        "Failed to generate emails: something went wrong"
    )
    assert result.to_gradio_tuple() == (
        "",
        "",
        "",
        "",
        "",
        "",
        "Failed to generate emails: something went wrong",
    )


@pytest.mark.asyncio
async def test_generate_emails_validates_required_inputs():
    result = await generate_emails(
        receiver_email="user@example.com",
        recipient_title="",
        product_context="SynthPilot context",
    )

    assert result.ready_to_send is False
    assert result.status == GENERATION_FAILED_STATUS.format(
        error=MISSING_INPUT_STATUS.format(fields="recipient / greeting")
    )


@pytest.mark.asyncio
async def test_generate_emails_success(
    mock_run_result,
    sample_drafts,
    sample_picker_output,
):
    draft_1, draft_2, draft_3 = sample_drafts

    async def fake_run(agent, message):
        if agent.name == "Sales Picker":
            return mock_run_result(sample_picker_output)
        if agent.name == "Professional Sales Agent":
            return mock_run_result(draft_1)
        if agent.name == "Engaging Sales Agent":
            return mock_run_result(draft_2)
        if agent.name == "Busy Sales Agent":
            return mock_run_result(draft_3)
        raise AssertionError(f"Unexpected agent: {agent.name}")

    with patch("flows.Runner.run", side_effect=fake_run):
        result = await generate_emails(
            receiver_email="user@example.com",
            recipient_title="Dear Leader",
            product_context="SynthPilot helps teams prioritize features.",
        )

    assert result.draft_1 == draft_1
    assert result.draft_2 == draft_2
    assert result.draft_3 == draft_3
    assert result.explanation == sample_picker_output.explanation
    assert result.selected_email == sample_picker_output.selected_email
    assert result.status == EMAIL_GENERATED_STATUS
    assert result.ready_to_send is True


@pytest.mark.asyncio
async def test_generate_emails_parses_structured_picker_output(mock_run_result, sample_drafts):
    draft_1, draft_2, draft_3 = sample_drafts
    picker_output = SalesPickerOutput(
        explanation="  Leading explanation  ",
        selected_email="  Selected email body  ",
    )

    async def fake_run(agent, message):
        if agent.name == "Sales Picker":
            return mock_run_result(picker_output)
        if agent.name == "Professional Sales Agent":
            return mock_run_result(draft_1)
        if agent.name == "Engaging Sales Agent":
            return mock_run_result(draft_2)
        if agent.name == "Busy Sales Agent":
            return mock_run_result(draft_3)
        raise AssertionError(f"Unexpected agent: {agent.name}")

    with patch("flows.Runner.run", side_effect=fake_run):
        result = await generate_emails(
            receiver_email="user@example.com",
            recipient_title="Dear Leader",
            product_context="Context",
        )

    assert result.explanation == "Leading explanation"
    assert result.selected_email == "Selected email body"


@pytest.mark.asyncio
async def test_generate_emails_rejects_incomplete_picker_output(
    mock_run_result,
    sample_drafts,
):
    draft_1, draft_2, draft_3 = sample_drafts
    incomplete = SalesPickerOutput(explanation="", selected_email="Email only")

    async def fake_run(agent, message):
        if agent.name == "Sales Picker":
            return mock_run_result(incomplete)
        if agent.name == "Professional Sales Agent":
            return mock_run_result(draft_1)
        if agent.name == "Engaging Sales Agent":
            return mock_run_result(draft_2)
        return mock_run_result(draft_3)

    with patch("flows.Runner.run", side_effect=fake_run):
        result = await generate_emails(
            receiver_email="user@example.com",
            recipient_title="Dear Leader",
            product_context="Context",
        )

    assert result.ready_to_send is False
    assert "incomplete selection" in result.status


@pytest.mark.asyncio
async def test_generate_emails_handles_runner_exceptions(mock_run_result):
    with patch(
        "flows.Runner.run",
        new_callable=AsyncMock,
        side_effect=RuntimeError("API unavailable"),
    ):
        result = await generate_emails(
            receiver_email="user@example.com",
            recipient_title="Dear Leader",
            product_context="Context",
        )

    assert result.ready_to_send is False
    assert result.status == GENERATION_FAILED_STATUS.format(
        error="Unexpected error: API unavailable"
    )
