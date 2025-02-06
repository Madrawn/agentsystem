"""
Set of classes that can be used to create agents that can run models.
preprocessors can be used to format messages before they are passed to the model,
also offers the possibility to chain multiple agents together or pipe in input from an arbitrary source.
postprocessors can be used to format the response from the model.
"""

import random
import re
from typing import Any, Callable, Type, TypeVar, cast
import functools

from torch import seed
from agentsystem.agents.preprocessor.preprocessor import (
    CallablePreprocessor,
    Preprocessor,
)
from agentsystem.agents.tools.tool import Tool
from agentsystem.models.Response import Response

from agentsystem.models.Model import ConsoleInputModel, Model


class Agent(Tool):
    preprocessor: Preprocessor
    postprocessor: Callable

    def __init__(
        self,
        *,
        model: "Model",
        preprocessor: Preprocessor = CallablePreprocessor.identity(),
        postprocessor: Callable = CallablePreprocessor.identity(),
        **extra_args,
    ):
        """Creates an Agent running with the given model.

        Args:
            model (Model): A Model that can process the prompt given in .run
            preprocessor (Callable): Function that processes system, prompt and prefix messages
            postprocessor (Callable[[str], Any]): Function that processes the response
            **extra_args: Additional arguments passed to the model
        """
        super().__init__(
            description="Agent for processing prompts through a model",
        )
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor
        self.model = model
        self.extra_args = extra_args

    def execute(
        self,
        system_message,
        prompt_message,
        prefix_message,
    ) -> Response:
        """Execute the model run with the given messages"""

        def execution():
            print(f"running {self}")
            (system, prompt, prefix), empty = self.preprocessor(
                system_message, prompt_message, prefix_message
            )
            response = self.model.run(system, prompt, prefix, **self.extra_args)
            args, kwargs = self.postprocessor(response())
            return args, kwargs

        return Response(execution)


class ChatAgent(Agent):
    """Differs from Agent in that it works with a list of messages instead of system, prompt and prefix messages."""

    def __init__(
        self,
        *,
        model: Model,
        preprocessor: Preprocessor = CallablePreprocessor.identity(),
        postprocessor: Callable[[str], Any] = lambda x: x,
        **extra_args,
    ):
        """Creates an AChatAgentgent running with the given model.

        Args:
            model (Model): A Model that can process the prompt given in .run

            preprocessor (Preprocessor, optional): A function that receives system, prompt and prefix messages
            and returns them. Use to for example format a prompt. Defaults to Preprocessor.after.

            postprocessor (Callable[[str], Any], optional): Function that receives a response and can change it. Defaults to lambdax:x.
        """
        self.model = model
        self.preprocessor = preprocessor
        self.postprocessor = postprocessor

        self.extra_args = extra_args


class ParsedAgent(Agent):
    """
    docstring
    """

    def __init__(self, regex_pattern, **parameter_list):
        super().__init__(**parameter_list)
        self.regex_pattern = regex_pattern
        self.postprocessor = lambda x: re.compile(regex_pattern).findall(x)


A = TypeVar("A")


class MultiShotAgent[A: Agent](Agent, metaclass=type):
    seed_generator = iter(lambda: random.randint(1, 99999), None)

    def __new__(
        cls,
        agent: Type[A] = Agent,
        seed_generator=iter(lambda: random.randint(1, 99999), None),
        *args,
        **kwargs: Model | Preprocessor | Callable[[str], Any] | Any,
    ) -> "MultiShotAgent":
        dynamic_multi_agent = type(
            f"MultiShot{agent.__name__}", (agent,), {"run": cls.run}
        )
        inst = cast(MultiShotAgent, dynamic_multi_agent(*args, **kwargs))
        inst.seed_generator = seed_generator
        return inst

    def run(self, **kwargs):
        seed = next(self.seed_generator)
        self.extra_args["seed"] = seed
        return super().run(**kwargs)


class AgentChain(Agent):

    preprocessor = Preprocessor.after

    def __init__(self, *agents: Agent, postprocessor=lambda x: x):
        self.agents = agents
        self.postprocessor = postprocessor

    def execute(
        self,
        system_message: str = "",
        prompt_message: str = "",
        prefix_message: str = "",
    ):
        for agent in self.agents:

            out = agent.run(
                system_message=system_message,
                prompt_message=prompt_message,
                prefix_message=prefix_message,
            ).__resolve()
        return Response(lambda: self.postprocessor(out))


class ParsedListAgentChain(Agent):
    r"""
    ParsedListAgentChain(
        regex_pattern=r'\d\. (.*?)[\. ]?\n',
        model=model,
        stream=True,
        **extra_args)
    """

    def __init__(self, regex_pattern, **parameter_list):
        """
        docstring
        """
        self.regex_pattern = regex_pattern
        super().__init__(**parameter_list)

    def execute(
        self,
        system_message: str = "",
        prompt_message: str = "",
        prefix_message: str = "",
    ):
        """
        docstring
        """
        prompt_agent = Agent(
            model=self.model,
            preprocessor=CallablePreprocessor(
                lambda sys, prompt, prefix: (
                    """A worker will be tasked to write some text and his response parsed with a regex pattern. Your task is to explain this to the worker.
                    Explain to the worker the format his answer has to be in and give an example output-string that would result in a list with three elements for given regex pattern:""",
                    prompt,
                    prefix,
                )
            ),
            **self.extra_args,
        ).run(
            prompt_message=f"re.compile(r'{self.regex_pattern}').findall(worker_response)"
        )

        list_agent = ParsedAgent(self.regex_pattern, model=self.model).run(
            system_message=prompt_agent(), prompt_message=prompt_message
        )
        return list_agent


class StatefulAgent(Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = {}

    def execute(
        self,
        system_message: str = "",
        prompt_message: str = "",
        prefix_message: str = "",
    ):
        # Include state in context
        context = {"state": self.state}
        # Update state based on response
        response = super().execute(system_message, prompt_message, prefix_message)
        return response


class ToolAgent(Agent):
    def __init__(self, *args, tools=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tools = tools or {}

    def register_tool(self, name, func):
        self.tools[name] = func

    def _format_tool_definitions(self):
        """Formats the tool definitions for inclusion in the system message."""
        return "\n".join(f"{name}: {func.__doc__}" for name, func in self.tools.items())

    def execute(
        self,
        system_message: str = "",
        prompt_message: str = "",
        prefix_message: str = "",
    ):
        # Inject tool definitions into system message
        tool_definitions = self._format_tool_definitions()
        enhanced_system = f"{system_message}\n\nAvailable tools:\n{tool_definitions}"
        return super().execute(enhanced_system, prompt_message, prefix_message)


class UserConsoleAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(model=ConsoleInputModel(), **kwargs)

    def execute(
        self,
        system_message: str = "",
        prompt_message: str = "",
        prefix_message: str = "",
    ):
        # Format context nicely for human reading

        return super().execute(
            system_message,
            prompt_message,
            prefix_message,
        )
