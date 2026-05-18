import json
import logging

import pytest
from pydantic import ValidationError

from sales_agent.compliance_logging import log_compliance_review
from sales_agent.config import COMPLIANCE_REJECTION_STATUS, EMAIL_GENERATED_STATUS
from sales_agent.flows import _handle_compliance_rejection, generate_emails
from sales_agent.messages import (
    compliance_review_message,
    format_compliance_review_for_picker,
    picker_input_message,
)
from sales_agent.schemas import (
    ComplianceReviewOutput,
    EmailComplianceAssessment,
    SalesPickerOutput,
)
from tests.conftest import FakeAgentRunner


def _assessment(
    email_index: int,
    *,
    notes: str,
    risk_flags: list[str] | None = None,
    professionalism: int = 4,
    grounding: int = 4,
    is_compliant: bool = True,
) -> EmailComplianceAssessment:
    return EmailComplianceAssessment(
        email_index=email_index,
        compliance_notes=notes,
        risk_flags=risk_flags or [],
        professionalism_score=professionalism,
        grounding_score=grounding,
        is_compliant=is_compliant,
    )


def _compliant_review(recommended_index: int = 1) -> ComplianceReviewOutput:
    return ComplianceReviewOutput(
        email_assessments=[
            _assessment(1, notes="Grounded in product context."),
            _assessment(2, notes="Professional tone."),
            _assessment(3, notes="Clear and concise."),
        ],
        recommended_email_index=recommended_index,
        overall_reasoning="All drafts are suitable for outbound sales.",
    )


def test_compliance_review_output_accepts_valid_structure():
    review = _compliant_review()

    assert review.recommended_email_index == 1
    assert len(review.email_assessments) == 3
    assert review.reject_all is False


def test_compliance_review_output_rejects_wrong_assessment_count():
    with pytest.raises(ValidationError):
        ComplianceReviewOutput(
            email_assessments=[
                _assessment(1, notes="Only one"),
            ],
            recommended_email_index=1,
            overall_reasoning="Invalid",
        )


def test_compliance_review_output_rejects_invalid_scores():
    with pytest.raises(ValidationError):
        EmailComplianceAssessment(
            email_index=1,
            compliance_notes="Bad score",
            professionalism_score=6,
            grounding_score=3,
            is_compliant=True,
        )


def test_compliance_review_flags_hallucinated_claims():
    review = ComplianceReviewOutput(
        email_assessments=[
            _assessment(
                1,
                notes="Claims 300% ROI without support in context.",
                risk_flags=["fabricated_metrics"],
                grounding=1,
                is_compliant=False,
            ),
            _assessment(2, notes="Acceptable."),
            _assessment(3, notes="Acceptable."),
        ],
        recommended_email_index=2,
        overall_reasoning="Email 1 contains unsupported metrics.",
    )

    assert review.email_assessments[0].risk_flags == ["fabricated_metrics"]
    assert review.email_assessments[0].is_compliant is False


def test_compliance_review_flags_spammy_wording():
    review = ComplianceReviewOutput(
        email_assessments=[
            _assessment(
                1,
                notes="Uses manipulative urgency.",
                risk_flags=["deceptive_urgency", "spam_language"],
                professionalism=2,
                is_compliant=False,
            ),
            _assessment(2, notes="Professional."),
            _assessment(3, notes="Professional."),
        ],
        recommended_email_index=2,
        overall_reasoning="Email 1 is too aggressive.",
    )

    assert "spam_language" in review.email_assessments[0].risk_flags


def test_compliance_review_flags_prompt_leakage():
    review = ComplianceReviewOutput(
        email_assessments=[
            _assessment(
                1,
                notes="Contains system prompt leakage.",
                risk_flags=["prompt_leakage"],
                is_compliant=False,
            ),
            _assessment(
                2,
                notes="Contains placeholder text.",
                risk_flags=["unresolved_placeholder"],
                is_compliant=False,
            ),
            _assessment(3, notes="Clean draft."),
        ],
        recommended_email_index=3,
        overall_reasoning="Emails 1 and 2 have integrity issues.",
    )

    formatted = format_compliance_review_for_picker(review)

    assert "prompt_leakage" in formatted
    assert "unresolved_placeholder" in formatted


def test_reject_all_sets_reject_all_property():
    review = ComplianceReviewOutput(
        email_assessments=[
            _assessment(1, notes="Fabricated customer.", is_compliant=False),
            _assessment(2, notes="Fake guarantee.", is_compliant=False),
            _assessment(3, notes="Unsupported legal claim.", is_compliant=False),
        ],
        recommended_email_index=0,
        overall_reasoning="All drafts must be rejected.",
    )

    assert review.reject_all is True


def test_handle_compliance_rejection_returns_none_for_compliant_review():
    assert _handle_compliance_rejection(_compliant_review()) is None


def test_handle_compliance_rejection_blocks_reject_all():
    review = ComplianceReviewOutput(
        email_assessments=[
            _assessment(1, notes="Bad", is_compliant=False),
            _assessment(2, notes="Bad", is_compliant=False),
            _assessment(3, notes="Bad", is_compliant=False),
        ],
        recommended_email_index=0,
        overall_reasoning="Reject all drafts.",
    )

    result = _handle_compliance_rejection(review)

    assert result is not None
    assert result.ready_to_send is False
    assert result.status == COMPLIANCE_REJECTION_STATUS


def test_handle_compliance_rejection_blocks_all_non_compliant():
    review = ComplianceReviewOutput(
        email_assessments=[
            _assessment(1, notes="Bad", is_compliant=False),
            _assessment(2, notes="Bad", is_compliant=False),
            _assessment(3, notes="Bad", is_compliant=False),
        ],
        recommended_email_index=2,
        overall_reasoning="No compliant options despite index suggestion.",
    )

    result = _handle_compliance_rejection(review)

    assert result is not None
    assert result.status == COMPLIANCE_REJECTION_STATUS


def test_compliance_review_message_includes_context_and_drafts():
    message = compliance_review_message(
        product_context="Acme helps teams track churn.",
        draft_1="Draft one",
        draft_2="Draft two",
        draft_3="Draft three",
    )

    assert "Acme helps teams track churn." in message
    assert "Draft one" in message
    assert "Email 1 (Professional draft)" in message


def test_picker_input_message_includes_compliance_findings():
    review = _compliant_review()
    message = picker_input_message("D1", "D2", "D3", review)

    assert "D1" in message
    assert "Compliance review findings" in message
    assert "Reviewer recommended email index: 1" in message


def test_log_compliance_review_emits_structured_log(caplog):
    review = _compliant_review()

    with caplog.at_level(logging.INFO):
        log_compliance_review(review)

    assert len(caplog.records) == 1
    logged = json.loads(caplog.records[0].message.split("\n", 1)[1])
    assert logged["recommended_email_index"] == 1


@pytest.mark.asyncio
async def test_generate_emails_runs_compliance_before_picker(
    mock_run_result,
    sample_drafts,
    sample_compliance_review,
    sample_picker_output,
):
    draft_1, draft_2, draft_3 = sample_drafts

    async def fake_run(agent, message):
        if agent.name == "Compliance Reviewer":
            return mock_run_result(sample_compliance_review)
        if agent.name == "Sales Picker":
            return mock_run_result(sample_picker_output)
        if agent.name == "Professional Sales Agent":
            return mock_run_result(draft_1)
        if agent.name == "Engaging Sales Agent":
            return mock_run_result(draft_2)
        if agent.name == "Busy Sales Agent":
            return mock_run_result(draft_3)
        raise AssertionError(f"Unexpected agent: {agent.name}")

    runner = FakeAgentRunner(fake_run)
    result = await generate_emails(
        receiver_email="user@example.com",
        recipient_title="Dear Leader",
        product_context="SynthPilot helps teams prioritize features.",
        runner=runner,
    )

    assert result.ready_to_send is True
    assert result.status == EMAIL_GENERATED_STATUS
    assert "Reviewer recommended email index" in result.compliance_summary
    assert len(runner.calls) == 5

    compliance_call = runner.calls[3]
    picker_call = runner.calls[4]
    assert compliance_call[0].name == "Compliance Reviewer"
    assert "SynthPilot helps teams prioritize features." in compliance_call[1]
    assert "Compliance review findings" in picker_call[1]


@pytest.mark.asyncio
async def test_generate_emails_stops_when_reviewer_rejects_all(
    mock_run_result,
    sample_drafts,
):
    draft_1, draft_2, draft_3 = sample_drafts
    rejection_review = ComplianceReviewOutput(
        email_assessments=[
            _assessment(
                1,
                notes="Invented Fortune 500 customer.",
                risk_flags=["invented_customer"],
                is_compliant=False,
            ),
            _assessment(
                2,
                notes="Fake guarantee.",
                risk_flags=["fake_guarantee"],
                is_compliant=False,
            ),
            _assessment(
                3,
                notes="Unsupported SOC 2 claim.",
                risk_flags=["unsupported_legal_claim"],
                is_compliant=False,
            ),
        ],
        recommended_email_index=0,
        overall_reasoning="All drafts contain policy violations.",
    )

    async def fake_run(agent, message):
        if agent.name == "Compliance Reviewer":
            return mock_run_result(rejection_review)
        if agent.name == "Professional Sales Agent":
            return mock_run_result(draft_1)
        if agent.name == "Engaging Sales Agent":
            return mock_run_result(draft_2)
        if agent.name == "Busy Sales Agent":
            return mock_run_result(draft_3)
        raise AssertionError(f"Picker should not run after rejection: {agent.name}")

    result = await generate_emails(
        receiver_email="user@example.com",
        recipient_title="Dear Leader",
        product_context="Context",
        runner=FakeAgentRunner(fake_run),
    )

    assert result.ready_to_send is False
    assert result.status == COMPLIANCE_REJECTION_STATUS
    assert result.selected_email == ""
