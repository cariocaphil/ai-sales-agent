from dataclasses import dataclass
from functools import lru_cache

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


@dataclass(frozen=True)
class AgentsBundle:
    professional: Agent
    engaging: Agent
    concise: Agent
    picker: Agent
    send_manager: Agent


@lru_cache
def get_agents() -> AgentsBundle:
    return AgentsBundle(
        professional=Agent(
            name="Professional Sales Agent",
            instructions=PROFESSIONAL_SALES_INSTRUCTIONS,
            model=MODEL,
        ),
        engaging=Agent(
            name="Engaging Sales Agent",
            instructions=ENGAGING_SALES_INSTRUCTIONS,
            model=MODEL,
        ),
        concise=Agent(
            name="Busy Sales Agent",
            instructions=CONCISE_SALES_INSTRUCTIONS,
            model=MODEL,
        ),
        picker=Agent(
            name="Sales Picker",
            instructions=SALES_PICKER_INSTRUCTIONS,
            output_type=SalesPickerOutput,
            model=MODEL,
        ),
        send_manager=Agent(
            name="Send Manager",
            instructions=SEND_MANAGER_INSTRUCTIONS,
            tools=[send_email],
            model=MODEL,
        ),
    )


def clear_agents_cache() -> None:
    """Clear cached agents. Intended for tests."""
    get_agents.cache_clear()
