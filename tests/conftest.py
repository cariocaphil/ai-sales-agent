import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import sales_agent.config  # noqa: F401 — load environment variables for tests
from sales_agent.schemas import (
    ComplianceReviewOutput,
    EmailComplianceAssessment,
    SalesPickerOutput,
)


@pytest.fixture
def mock_run_result():
    def _factory(final_output):
        return SimpleNamespace(final_output=final_output)

    return _factory


@pytest.fixture
def sample_picker_output():
    return SalesPickerOutput(
        explanation="Clear value proposition and concise call to action.",
        selected_email="Dear Product Leader,\n\nSynthPilot can help your team.\n\nBest,\nSales",
    )


@pytest.fixture
def sample_compliance_review():
    return ComplianceReviewOutput(
        email_assessments=[
            EmailComplianceAssessment(
                email_index=1,
                compliance_notes="Grounded and professional.",
                risk_flags=[],
                professionalism_score=5,
                grounding_score=5,
                is_compliant=True,
            ),
            EmailComplianceAssessment(
                email_index=2,
                compliance_notes="Engaging and accurate.",
                risk_flags=[],
                professionalism_score=4,
                grounding_score=4,
                is_compliant=True,
            ),
            EmailComplianceAssessment(
                email_index=3,
                compliance_notes="Concise and clear.",
                risk_flags=[],
                professionalism_score=4,
                grounding_score=4,
                is_compliant=True,
            ),
        ],
        recommended_email_index=1,
        overall_reasoning="Email 1 is the most grounded and professional.",
    )


@pytest.fixture
def sample_drafts():
    return (
        "Professional draft body",
        "Engaging draft body",
        "Concise draft body",
    )


@pytest.fixture
def sendgrid_env(monkeypatch):
    monkeypatch.setenv("SENDGRID_API_KEY", "test-api-key")
    monkeypatch.setenv("SENDGRID_FROM_EMAIL", "sender@example.com")


@pytest.fixture
def mock_sendgrid_client(monkeypatch):
    mock_response = MagicMock(status_code=202)
    mock_post = MagicMock(return_value=mock_response)
    mock_send = MagicMock()
    mock_send.post = mock_post
    mock_mail = MagicMock()
    mock_mail.send = mock_send
    mock_client = MagicMock()
    mock_client.mail = mock_mail
    mock_sg = MagicMock()
    mock_sg.client = mock_client
    mock_client_class = MagicMock(return_value=mock_sg)

    monkeypatch.setattr(
        "sales_agent.email_service.sendgrid.SendGridAPIClient",
        mock_client_class,
    )
    return mock_client_class, mock_post


def parse_json_output(raw: str) -> SalesPickerOutput:
    return SalesPickerOutput.model_validate(json.loads(raw))


class FakeAgentRunner:
    """Injected test double for AgentRunner."""

    def __init__(self, run_impl):
        self._run_impl = run_impl
        self.calls: list[tuple] = []

    async def run(self, agent, message):
        self.calls.append((agent, message))
        return await self._run_impl(agent, message)
