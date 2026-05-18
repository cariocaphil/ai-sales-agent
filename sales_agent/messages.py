from sales_agent.prompts import EMAIL_GENERATION_MESSAGE_TEMPLATE
from sales_agent.schemas import ComplianceReviewOutput


def email_generation_message(recipient_title: str, product_context: str) -> str:
    return EMAIL_GENERATION_MESSAGE_TEMPLATE.format(
        recipient_title=recipient_title,
        product_context=product_context,
    ).strip()


def compliance_review_message(
    product_context: str,
    draft_1: str,
    draft_2: str,
    draft_3: str,
) -> str:
    return f"""
Review the following cold sales email drafts for compliance and quality.

Product or service context (source material only):
{product_context}

Email 1 (Professional draft):
{draft_1}

Email 2 (Engaging draft):
{draft_2}

Email 3 (Concise draft):
{draft_3}
""".strip()


def format_compliance_review_for_picker(review: ComplianceReviewOutput) -> str:
    lines = [
        f"Overall reasoning: {review.overall_reasoning}",
        f"Reviewer recommended email index: {review.recommended_email_index}",
        "",
    ]

    for assessment in review.email_assessments:
        flags = ", ".join(assessment.risk_flags) if assessment.risk_flags else "none"
        lines.extend(
            [
                f"Email {assessment.email_index}:",
                f"- Compliant: {assessment.is_compliant}",
                f"- Professionalism score: {assessment.professionalism_score}/5",
                f"- Grounding score: {assessment.grounding_score}/5",
                f"- Risk flags: {flags}",
                f"- Notes: {assessment.compliance_notes}",
                "",
            ]
        )

    return "\n".join(lines).strip()


def picker_input_message(
    draft_1: str,
    draft_2: str,
    draft_3: str,
    compliance_review: ComplianceReviewOutput,
) -> str:
    review_summary = format_compliance_review_for_picker(compliance_review)

    return f"""
Cold sales emails:

Email 1:
{draft_1}

Email 2:
{draft_2}

Email 3:
{draft_3}

Compliance review findings:
{review_summary}
""".strip()


def send_email_message(receiver_email: str, selected_email: str) -> str:
    return f"""
Send this approved email exactly as written.

Receiver email:
{receiver_email}

Approved email:
{selected_email}
"""
