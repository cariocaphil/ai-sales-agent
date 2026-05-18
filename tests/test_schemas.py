import json

import pytest
from pydantic import ValidationError

from schemas import GenerationResult, SalesPickerOutput
from tests.conftest import parse_json_output


def test_sales_picker_output_accepts_valid_json():
    payload = {
        "explanation": "Strong opening and clear CTA.",
        "selected_email": "Dear Alex,\n\nWe help teams ship faster.\n\nBest,\nSales",
    }

    result = SalesPickerOutput.model_validate_json(json.dumps(payload))

    assert result.explanation == payload["explanation"]
    assert result.selected_email == payload["selected_email"]


def test_sales_picker_output_rejects_missing_fields():
    with pytest.raises(ValidationError):
        SalesPickerOutput.model_validate({"explanation": "Only one field"})


def test_sales_picker_output_rejects_wrong_field_types():
    with pytest.raises(ValidationError):
        SalesPickerOutput.model_validate(
            {"explanation": 123, "selected_email": "Hello"}
        )


def test_parse_json_output_helper():
    raw = json.dumps(
        {
            "explanation": "Best tone for executives.",
            "selected_email": "Hello there",
        }
    )

    result = parse_json_output(raw)

    assert isinstance(result, SalesPickerOutput)
    assert result.selected_email == "Hello there"


def test_generation_result_to_gradio_tuple_duplicates_selected_email():
    result = GenerationResult(
        draft_1="d1",
        draft_2="d2",
        draft_3="d3",
        explanation="because",
        selected_email="email body",
        status="ok",
        ready_to_send=True,
    )

    assert result.to_gradio_tuple() == (
        "d1",
        "d2",
        "d3",
        "because",
        "email body",
        "email body",
        "ok",
    )


def test_sales_picker_output_strips_are_applied_in_flow_not_schema():
    output = SalesPickerOutput(
        explanation="  spaced  ",
        selected_email="  email body  ",
    )
    assert output.explanation == "  spaced  "
    assert output.selected_email == "  email body  "
