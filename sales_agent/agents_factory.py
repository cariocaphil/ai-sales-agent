from agents import Agent

from sales_agent.email_service import send_email
from sales_agent.prompts import (
    CONCISE_SALES_INSTRUCTIONS,
    ENGAGING_SALES_INSTRUCTIONS,
    PROFESSIONAL_SALES_INSTRUCTIONS,
    SALES_PICKER_INSTRUCTIONS,
    SEND_MANAGER_INSTRUCTIONS,
)
from sales_agent.schemas import SalesPickerOutput

MODEL = "gpt-4o-mini"

sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=PROFESSIONAL_SALES_INSTRUCTIONS,
    model=MODEL,
)

sales_agent2 = Agent(
    name="Engaging Sales Agent",
    instructions=ENGAGING_SALES_INSTRUCTIONS,
    model=MODEL,
)

sales_agent3 = Agent(
    name="Busy Sales Agent",
    instructions=CONCISE_SALES_INSTRUCTIONS,
    model=MODEL,
)

sales_picker = Agent(
    name="Sales Picker",
    instructions=SALES_PICKER_INSTRUCTIONS,
    output_type=SalesPickerOutput,
    model=MODEL,
)

send_manager = Agent(
    name="Send Manager",
    instructions=SEND_MANAGER_INSTRUCTIONS,
    tools=[send_email],
    model=MODEL,
)
