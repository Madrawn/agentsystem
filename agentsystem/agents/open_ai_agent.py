import json
import os
from pathlib import Path
from typing import Any
from openai import AzureOpenAI
from agentsystem.agents.agents import Agent
from agentsystem.agents.tools.tool import Tool
from agentsystem.models.Model import Model
from openai.types.chat.chat_completion_tool_choice_option_param import (
    ChatCompletionToolChoiceOptionParam,
)
from agentsystem.models.Response import Response


class OpenAIModel(Model):

    def __init__(self, model=None, *args, **kwargs):
        super().__init__(model=self, *args, **kwargs)
        self.client = None
        self.deployment_name = None
        # Initialize the Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_INFERENCE_ENDPOINT"),
            api_key=os.getenv("AZURE_INFERENCE_CREDENTIAL"),
            api_version="2024-05-01-preview",
        )

        # Define the deployment you want to use for your chat completions API calls
        self.deployment_name = os.getenv("DEPLOYMENT")

    def format(self, system_message, prompt_message, prefix_message) -> str:
        return ""

    def _run(
        self,
        prompt: str = "",
        messages=None,
        tools=[],
        tool_choice: ChatCompletionToolChoiceOptionParam = "auto",
        **extra_args,
    ) -> Any:
        if messages is None:
            messages = []

        if not self.deployment_name:
            return "<Error: Deployment name is not set>"

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            **extra_args,
        )

        if response.choices and response.choices[0].message:
            return response.choices[0].message
        return "<Error: No response from the model>"


class OpenAIToolChat(Agent):
    messages: list[dict] = []

    def __init__(self, model, *args, **kwargs):
        super().__init__(model=model, *args, **kwargs)
        self.tools: list[Tool] = []
        self.messages: list[dict] = []
        self._tool_map = {}  # Map tool names to tool instances

    def add_tool(self, tool: Tool):
        """Add a tool to the agent and update the tool map."""
        self.tools.append(tool)
        # Map the tool name to the tool instance for easy lookup
        tool_desc = tool.get_openai_description()
        self._tool_map[tool_desc["function"]["name"]] = tool

    def execute(
        self,
        system_message: str = "",
        prompt_message: str = "",
        prefix_message: str = "",
    ):
        """Execute the conversation flow with tools."""
        # Initialize the conversation with the user's input
        if system_message:
            self.messages.append({"role": "system", "content": system_message})
        if prompt_message:
            self.messages.append({"role": "user", "content": prompt_message})

        return Response(lambda: self._run_conversation())

    def _run_conversation(self) -> str:
        """Internal method to handle the conversation flow with tools."""
        while True:
            # Get model's response
            response = self.model.run(
                system_message="",
                prompt_message="",
                prefix_message="",
                frequency_penalty=0.2,
                messages=self.messages,
                tools=self.list_open_ai_descriptions() if self.tools else None,
                tool_choice="auto" if self.tools else "None",
            )()
            # Add model's response to conversation history
            self.messages.append(response)
            tool_calls = []
            # Check for tool calls
            if response.tool_calls:
                tool_calls = response.tool_calls
            else:
                return response
            for tool_call in tool_calls:
                # Get the corresponding tool
                tool = self._tool_map.get(tool_call.function.name)
                if not tool:
                    continue

                # Parse and execute the tool
                try:
                    args = json.loads(tool_call.function.arguments)
                    result = tool.execute(**args)()

                    # Add tool response to conversation
                    self.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": str(result),
                        }
                    )
                except Exception as e:
                    # Handle tool execution errors
                    self.messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": tool_call.function.name,
                            "content": f"Error executing tool: {str(e)}",
                        }
                    )

            # If no tool calls were made, return the final response
            if not tool_calls:
                break
            import logging

            logging.info(f"Tool calls: {tool_calls}")

        # Get final response incorporating tool results
        final_response = self.model.run(
            system_message="",
            prompt_message="",
            prefix_message="",
            frequency_penalty=0.1,
            temperature=0.2,
            messages=self.messages,
            tools=self.list_open_ai_descriptions(),
        )
        final_response_content = final_response()
        Path("./response.json").write_text(json.dumps(self.messages, indent=2))
        return final_response_content

    def list_open_ai_descriptions(self):
        return [tool.get_openai_description() for tool in self.tools]
