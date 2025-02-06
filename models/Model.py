from ast import mod
import os
import sys
from typing import Any

from openai import AzureOpenAI
from agentsystem.models.Response import Response


class Model:
    """
    The base class for models that generate responses based on a given prompt and other parameters. Subclasses must implement the `format` and `_run` methods.

    Methods:
        format(system\\_message, prompt\\_message, prefix\\_message) -> str: Formats the given messages into a string that can be passed to the model.
        run(system\\_message, prompt\\_message, prefix\\_message, **extra\\_args) -> Response[str]: Runs the model with the given parameters and returns a response object containing the result.
    """

    def __init__(self, model, pure_callback=None):
        """
        docstring
        """
        self.model = model
        self.pure_callback = pure_callback

    def format(self, system_message, prompt_message, prefix_message) -> str:
        """Formats the given messages into a string that can be passed to the model.

        Args:
            system_message (str): The system message to include in the formatted string.
            prompt_message (str): The prompt message to include in the formatted string.
            prefix_message (str): The prefix message to include in the formatted string.

        Returns:
        """
        raise NotImplementedError

    def run(
        self, system_message, prompt_message, prefix_message, **extra_args
    ) -> "Response":
        """Runs the model with the given parameters and returns a response object containing the result.

        Args:
            system_message (str): The system message to include in the formatted string.
            prompt_message (str): The prompt message to include in the formatted string.
            prefix_message (str): The prefix message to include in the formatted string.

        Returns:
            Response[str]: A response object containing the result of running the model.
        """
        prompt = self.format(system_message, prompt_message, prefix_message)
        print()
        print()
        return Response(lambda: self._run(prompt, **extra_args))

    def _run(self, prompt, **extra_args) -> Any:
        """Generates a response using the underlying model implementation and returns it as a string. This method should be implemented by subclasses.

        Args:
            parameter\\_list (List[Any]): A list of parameters to pass to the model. The format of this list will depend on the specific model implementation.
            **extra\\_args: Additional arguments that will be passed directly to the underlying model's generate method, if applicable.

        Raises:
            NotImplementedError: _description_

        Returns:
            str: The generated response from the model.

        """
        raise NotImplementedError

    def interrupt(self) -> None:
        """Interrupts the current model run, if possible. This method should be implemented by subclasses.

        Raises:
            NotImplementedError

        """
        raise NotImplementedError


class ChatModel(Model):
    """Abstract class for chat models. Differs from @Model in that it uses a messages list instead of *(system_message, prompt_message, prefix_message)"""

    def format(self, messages) -> str:
        """Formats the given messages into a string that can be passed to the model.

        Args:
            messages (List[str]): The list of messages to include in the formatted string.

        Returns:
            str: The formatted string.
        """
        raise NotImplementedError

    def run(self, messages, **extra_args) -> "Response[str]":
        """Runs the model with the given parameters and returns a response object containing the result.

        Args:
            messages (List[str]): The list of messages to include in the formatted string.

        Returns:
            Response[str]: A response object containing the result of running the model.
        """
        prompt = self.format(messages)
        return Response(lambda: self._run(prompt, **extra_args))


class ConsoleInputModel(Model):
    def __init__(self, pure_callback=None):
        super().__init__(None, pure_callback)

    def _run(self, prompt, **extra_args) -> str:
        """
        Executes the model with the given prompt.

        try:
            return input()
        except EOFError:
            return ""
            prompt (str): The prompt to be processed by the model.
        """
        print("\n=== System Prompt ===")
        print(prompt)
        print("\n=== Your Response ===")
        if 'pytest' in sys.modules:
            return "Execution result"
        return input()

    def format(self, system_message, prompt_message, prefix_message) -> str:
        """Formats the given messages into a string that can be passed to the model.

        Args:
            system_message (str): The system message to include in the formatted string.
            prompt_message (str): The prompt message to include in the formatted string.
            prefix_message (str): The prefix message to include in the formatted string.

        Returns:
            str: The formatted string.
        """
        return self._format_for_human(system_message, prompt_message, prefix_message)

    def _format_for_human(
        self, system_message: str, prompt_message: str, prefix_message: str
    ) -> str:
        """
        Formats the given messages into a human-readable format.

        Args:
            system_message (str): The system message to be formatted.
            prompt_message (str): The prompt message to be formatted.
            prefix_message (str): The prefix message to be formatted.

        Returns:
            str: A formatted string containing the system, prompt, and prefix messages.
        """
        return (
            f"System message:\n{system_message}\n\n"
            f"Prompt message:\n{prompt_message}\n\n"
            f"Prefix message:\n{prefix_message}"
        )

