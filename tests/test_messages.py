from sales_agent.messages import (
    compliance_review_message,
    email_generation_message,
    format_compliance_review_for_picker,
)
from sales_agent.schemas import ComplianceReviewOutput, EmailComplianceAssessment


def test_email_generation_message_injects_product_context():
    message = email_generation_message(
        recipient_title="Dear Alex",
        product_context="Acme Analytics helps teams track churn.",
    )

    assert "Dear Alex" in message
    assert "Acme Analytics helps teams track churn." in message
    assert "Product or service context (source material only" in message
    assert "SynthPilot" not in message


def test_compliance_review_message_lists_all_drafts():
    message = compliance_review_message(
        product_context="Product facts only.",
        draft_1="First",
        draft_2="Second",
        draft_3="Third",
    )

    assert "Product facts only." in message
    assert "Email 3 (Concise draft):" in message
    assert "Third" in message


def test_format_compliance_review_for_picker_includes_scores():
    review = ComplianceReviewOutput(
        email_assessments=[
            EmailComplianceAssessment(
                email_index=1,
                compliance_notes="OK",
                risk_flags=[],
                professionalism_score=5,
                grounding_score=4,
                is_compliant=True,
            ),
            EmailComplianceAssessment(
                email_index=2,
                compliance_notes="OK",
                professionalism_score=4,
                grounding_score=4,
                is_compliant=True,
            ),
            EmailComplianceAssessment(
                email_index=3,
                compliance_notes="OK",
                professionalism_score=4,
                grounding_score=4,
                is_compliant=True,
            ),
        ],
        recommended_email_index=1,
        overall_reasoning="Email 1 wins.",
    )

    formatted = format_compliance_review_for_picker(review)

    assert "Professionalism score: 5/5" in formatted
    assert "Grounding score: 4/5" in formatted
