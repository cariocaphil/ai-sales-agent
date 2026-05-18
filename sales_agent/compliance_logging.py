import json
import logging

from sales_agent.schemas import ComplianceReviewOutput

logger = logging.getLogger(__name__)


def log_compliance_review(review: ComplianceReviewOutput) -> None:
    """Log structured compliance review output for development inspection."""
    logger.info(
        "Compliance review completed:\n%s",
        json.dumps(review.model_dump(), indent=2),
    )
