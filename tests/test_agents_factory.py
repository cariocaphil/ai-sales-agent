from unittest.mock import patch

from agents import Agent

from sales_agent.agents_factory import AgentsBundle, clear_agents_cache, get_agents


def setup_function():
    clear_agents_cache()


def test_get_agents_returns_cached_bundle():
    first = get_agents()
    second = get_agents()

    assert first is second
    assert isinstance(first, AgentsBundle)


def test_get_agents_builds_all_agents_lazily():
    with patch("sales_agent.agents_factory.Agent", wraps=Agent) as mock_agent:
        clear_agents_cache()
        bundle = get_agents()

    assert mock_agent.call_count == 6
    assert bundle.professional.name == "Professional Sales Agent"
    assert bundle.engaging.name == "Engaging Sales Agent"
    assert bundle.concise.name == "Busy Sales Agent"
    assert bundle.compliance_reviewer.name == "Compliance Reviewer"
    assert bundle.picker.name == "Sales Picker"
    assert bundle.send_manager.name == "Send Manager"


def test_importing_flows_does_not_instantiate_agents():
    import importlib

    clear_agents_cache()

    with patch("sales_agent.agents_factory.Agent") as mock_agent:
        import sales_agent.flows as flows_module

        importlib.reload(flows_module)

    mock_agent.assert_not_called()
