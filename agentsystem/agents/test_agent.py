import pytest
from unittest.mock import MagicMock, patch
from agents import Agent, AgentChain
from agentsystem.agents.preprocessor.preprocessor import CallablePreprocessor
from agentsystem.agents.tools.tool import Tool
from agentsystem.models.Model import ConsoleInputModel


@pytest.fixture
def agent():
    model = MagicMock()
    preprocessor = MagicMock(wraps=CallablePreprocessor.identity())
    extra_args = {"key": "value"}
    return Agent(model=model, preprocessor=preprocessor, extra_args=extra_args)


@pytest.fixture
def agent_chain():
    agent1 = MagicMock()
    agent2 = MagicMock()
    return AgentChain(agent1, agent2)


def test_agent_run(agent):
    (
        system_message,
        prompt_message,
        prefix_message,
        model_run_return_value,
        expected_run_args,
    ) = configure_agent_execution(agent)

    result, _ = agent.run(
        system_message=system_message,
        prompt_message=prompt_message,
        prefix_message=prefix_message,
    )()
    expected_run_args = {
        "system_message": system_message,
        "prompt_message": prompt_message,
        "prefix_message": prefix_message,
    }

    agent.preprocessor.assert_called_once_with(*(list(expected_run_args.values())))
    agent.model.run.assert_called_once_with(
        *(list(expected_run_args.values())), **agent.extra_args
    )
    assert result[0] == model_run_return_value


def test_agent_as_tool_run(agent):
    (
        system_message,
        prompt_message,
        prefix_message,
        model_run_return_value,
        expected_run_args,
    ) = configure_agent_execution(agent)

    def helper(agent: Tool):
        return agent.run(
            system_message=system_message,
            prompt_message=prompt_message,
            prefix_message=prefix_message,
        )()

    result, empty = helper(agent)

    expected_run_args = {
        "system_message": system_message,
        "prompt_message": prompt_message,
        "prefix_message": prefix_message,
    }
    agent.preprocessor.assert_called_once_with(*(list(expected_run_args.values())))
    agent.model.run.assert_called_once_with(
        *(list(expected_run_args.values())), **agent.extra_args
    )
    assert result[0] == model_run_return_value


def configure_agent_execution(agent):
    system_message = "system message"
    prompt_message = "prompt message"
    prefix_message = "prefix message"

    model_run_return_value = "model run result"
    agent.model.run.return_value.return_value = model_run_return_value

    expected_run_args = {
        system_message,
        prompt_message,
        prefix_message,
    }

    # expected_run_args = {
    #     "system_message": system_message,
    #     "prompt_message": prompt_message,
    #     "prefix_message": prefix_message,
    # }
    return (
        system_message,
        prompt_message,
        prefix_message,
        model_run_return_value,
        expected_run_args,
    )


from agentsystem.agents.agents import UserConsoleAgent


class TestUserConsoleAgent:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.agent = UserConsoleAgent()

    def test_format_for_human(self):
        system_message = "System message content"
        prompt_message = "Prompt message content"
        prefix_message = "Prefix message content"
        expected_output = (
            "System message:\nSystem message content\n\n"
            "Prompt message:\nPrompt message content\n\n"
            "Prefix message:\nPrefix message content"
        )
        result = self.agent.model._format_for_human(
            system_message, prompt_message, prefix_message
        )
        assert result == expected_output


if __name__ == "__main__":
    pytest.main()
