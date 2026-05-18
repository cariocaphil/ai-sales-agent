from typing import Any, Protocol

from agents import Runner


class AgentRunner(Protocol):
    async def run(self, agent: Any, message: str) -> Any:
        """Run an agent with the given input message."""


class DefaultAgentRunner:
    async def run(self, agent: Any, message: str) -> Any:
        return await Runner.run(agent, message)


default_runner = DefaultAgentRunner()
