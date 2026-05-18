from unittest.mock import AsyncMock, patch

import pytest

from sales_agent.runner import DefaultAgentRunner


@pytest.mark.asyncio
async def test_default_runner_delegates_to_agents_runner():
    agent = object()
    message = "test message"
    expected = object()

    with patch(
        "sales_agent.runner.Runner.run",
        new_callable=AsyncMock,
        return_value=expected,
    ) as mock_run:
        result = await DefaultAgentRunner().run(agent, message)

    assert result is expected
    mock_run.assert_awaited_once_with(agent, message)
