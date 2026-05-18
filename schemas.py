from dataclasses import dataclass

from pydantic import BaseModel


class SalesPickerOutput(BaseModel):
    explanation: str
    selected_email: str


@dataclass(frozen=True)
class GenerationResult:
    draft_1: str = ""
    draft_2: str = ""
    draft_3: str = ""
    explanation: str = ""
    selected_email: str = ""
    status: str = ""
    ready_to_send: bool = False

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
