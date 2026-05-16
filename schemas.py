from pydantic import BaseModel


class SalesPickerOutput(BaseModel):
    explanation: str
    selected_email: str
