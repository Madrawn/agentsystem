from typing import Any, Callable


class Preprocessor:
    """The base class for preprocessors that format given system, prompt and prefix messages. Subclasses need to implement the `_process` method."""

    def after(self, *args, **kwargs):
        """Formats the given messages and returns them.

        Args:
            system_message (str): The system message to format.
            prompt_message (str): The prompt message to format.
            prefix_message (str): The prefix message to format.

        Returns:
            tuple[str, str, str]: The formatted system, prompt and prefix messages.
        """
        return args, kwargs

    def then(self, preprocessor: Callable):
        """Sets the after method to be called with the result of the given function.

        Args:
            preprocessor (Callable[[str, str, str], tuple[str, str, str]]): A function that processes system, prompt and prefix messages and returns them.

        Returns:
            Callable[[str, str, str], tuple[str, str, str]]: The updated after method.
        """

        def wrapped_after(*args, **kwargs) -> Any:
            return preprocessor(*args, **kwargs)

        self.after = wrapped_after
        return wrapped_after

    def __call__(self, *args, **kwargs):
        """Processes the given system, prompt and prefix messages using the current preprocessor.

        Returns:
            tuple[str, str, str]: The processed system, prompt and prefix messages.
        """
        args, kwargs = self._process(*args, **kwargs)
        return self.after(*args, **kwargs)

    def _process(self, *args, **kwargs):
        """To be implemented by subclasses to process given messages.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError


class SimpleTemplatePreprocessor(Preprocessor):
    """A preprocessor that formats given messages using given templates."""

    def __init__(
        self,
        system_message_template: str = "{system_message}",
        prompt_message_template: str = "{prompt_message}",
        prefix_message_template: str = "{prefix_message}",
    ) -> None:
        """Creates a preprocessor that formats messages using given templates.

        Args:
            system_message_template (str): The template to use for the system message. Defaults to "{system_message}".
            prompt_message_template (str): The template to use for the prompt message. Defaults to "{prompt_message}".
            prefix_message_template (str): The template to use for the prefix message. Defaults to "{prefix_message}".
        """
        self.system_message_template = system_message_template
        self.prompt_message_template = prompt_message_template
        self.prefix_message_template = prefix_message_template
        super().__init__()

    def _process(self, system_message, prompt_message, prefix_message, **kwargs):
        """Formats the given messages using given templates.

        Args:
            system_message (str): The system message to format.
            prompt_message (str): The prompt message to format.
            prefix_message (str): The prefix message to format.

        Returns:
            tuple[str, str, str]: The formatted system, prompt and prefix messages.
        """
        processed_messages = (
            self.system_message_template.format(system_message=system_message),
            self.prompt_message_template.format(prompt_message=prompt_message),
            self.prefix_message_template.format(prefix_message=prefix_message),
        )

        return processed_messages, kwargs


class CallablePreprocessor(Preprocessor):
    """A preprocessor that can be called like a function but maintains type safety."""

    def __init__(self, func: Callable[[str, str, str], Any]):
        self.func = func

    def _process(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @classmethod
    def identity(cls) -> "CallablePreprocessor":
        """Creates a default identity preprocessor."""

        def mirror(*args, **kwargs):
            return args, kwargs

        return cls(mirror)
