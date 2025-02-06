import pytest
from agentsystem.agents.preprocessor.preprocessor import SimpleTemplatePreprocessor


class TestSimpleTemplatePreprocessor:
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.preprocessor = SimpleTemplatePreprocessor()

    def test_default_templates(self):
        system_message = "This is a system message."
        prompt_message = "Please enter your input:"
        prefix_message = "> "
        result, empty = self.preprocessor(
            system_message, prompt_message, prefix_message
        )
        expected_system_message = system_message
        expected_prompt_message = prompt_message
        expected_prefix_message = prefix_message
        assert result == (
            expected_system_message,
            expected_prompt_message,
            expected_prefix_message,
        )

    def test_custom_templates(self):
        system_message_template = "System: {system_message}"
        prompt_message_template = "User: {prompt_message}"
        prefix_message_template = "> {prefix_message}"
        preprocessor = SimpleTemplatePreprocessor(
            system_message_template, prompt_message_template, prefix_message_template
        )
        system_message = "This is a system message."
        prompt_message = "Please enter your input:"
        prefix_message = "> "
        result, empty = preprocessor(system_message, prompt_message, prefix_message)
        expected_system_message = f"System: {system_message}"
        expected_prompt_message = f"User: {prompt_message}"
        expected_prefix_message = f"> {prefix_message}"
        assert result == (
            expected_system_message,
            expected_prompt_message,
            expected_prefix_message,
        )


if __name__ == "__main__":
    pytest.main()
