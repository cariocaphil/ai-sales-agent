from sales_agent.messages import email_generation_message


def test_email_generation_message_injects_product_context():
    message = email_generation_message(
        recipient_title="Dear Alex",
        product_context="Acme Analytics helps teams track churn.",
    )

    assert "Dear Alex" in message
    assert "Acme Analytics helps teams track churn." in message
    assert "Product or service context:" in message
    assert "SynthPilot" not in message
