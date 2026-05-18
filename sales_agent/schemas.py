from dataclasses import dataclass

from pydantic import BaseModel, Field, field_validator


class SalesPickerOutput(BaseModel):
    explanation: str
    selected_email: str


class EmailComplianceAssessment(BaseModel):
    email_index: int = Field(
        description="1-based index of the draft email (1, 2, or 3)."
    )
    compliance_notes: str
    risk_flags: list[str] = Field(default_factory=list)
    professionalism_score: int = Field(ge=1, le=5)
    grounding_score: int = Field(ge=1, le=5)
    is_compliant: bool


class ComplianceReviewOutput(BaseModel):
    email_assessments: list[EmailComplianceAssessment]
    recommended_email_index: int = Field(
        description="1-based index of the best compliant draft, or 0 to reject all."
    )
    overall_reasoning: str

    @field_validator("email_assessments")
    @classmethod
    def validate_assessment_count(cls, value: list[EmailComplianceAssessment]) -> list:
        if len(value) != 3:
            raise ValueError("email_assessments must contain exactly 3 entries.")
        return value

    @property
    def reject_all(self) -> bool:
        return self.recommended_email_index == 0


@dataclass(frozen=True)
class GenerationResult:
    draft_1: str = ""
    draft_2: str = ""
    draft_3: str = ""
    explanation: str = ""
    selected_email: str = ""
    status: str = ""
    ready_to_send: bool = False
    compliance_summary: str = ""

    @classmethod
    def failure(cls, status: str) -> "GenerationResult":
        return cls(status=status, ready_to_send=False)

    def to_gradio_tuple(self) -> tuple[str, str, str, str, str, str, str]:
        return (
            self.draft_1,
            self.draft_2,
            self.draft_3,
            self.explanation,
            self.selected_email,
            self.selected_email,
            self.status,
        )
