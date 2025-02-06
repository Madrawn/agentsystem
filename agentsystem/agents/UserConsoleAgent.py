from dataclasses import dataclass
from typing import Optional, Any, Dict, List
import asyncio
from enum import Enum
import json

class PromptType(Enum):
    TEXT = "text"
    JSON = "json"
    CONFIRM = "confirm"
    FILE = "file"

@dataclass
class PromptRequest:
    prompt: str
    type: PromptType = PromptType.TEXT
    context: Optional[Dict[str, Any]] = None
    options: Optional[List[str]] = None
    schema: Optional[Dict[str, Any]] = None

@dataclass
class PromptResponse:
    content: Any
    metadata: Dict[str, Any] = None
    error: Optional[str] = None

class UserConsoleAgent:
    def __init__(self, name: str = "user"):
        self.name = name
        self.context: Dict[str, Any] = {}
        self.history: List[tuple[PromptRequest, PromptResponse]] = []

    async def prompt(self, request: PromptRequest) -> PromptResponse:
        """Main entry point for prompting the user"""
        try:
            # Print context if available
            if request.context:
                print("\nContext:")
                print(json.dumps(request.context, indent=2))
                print()

            # Print the main prompt
            print(f"\n{request.prompt}")

            # Handle different prompt types
            response = await self._handle_prompt_type(request)
            
            # Store in history
            self.history.append((request, response))
            
            return response

        except Exception as e:
            return PromptResponse(content=None, error=str(e))

    async def _handle_prompt_type(self, request: PromptRequest) -> PromptResponse:
        """Handle different types of prompts"""
        if request.type == PromptType.CONFIRM:
            return await self._handle_confirmation(request)
        elif request.type == PromptType.JSON:
            return await self._handle_json(request)
        elif request.type == PromptType.FILE:
            return await self._handle_file(request)
        else:  # Default to TEXT
            return await self._handle_text(request)

    async def _handle_text(self, request: PromptRequest) -> PromptResponse:
        """Handle free-form text input"""
        if request.options:
            print("\nOptions:")
            for i, option in enumerate(request.options, 1):
                print(f"{i}. {option}")
            print("\nEnter number or text: ")
        
        response = await self._get_input()
        
        if request.options:
            try:
                idx = int(response) - 1
                if 0 <= idx < len(request.options):
                    response = request.options[idx]
            except ValueError:
                pass  # Keep original response if not a valid number

        return PromptResponse(content=response)

    async def _handle_confirmation(self, request: PromptRequest) -> PromptResponse:
        """Handle yes/no confirmation"""
        print("[y/n]: ", end="")
        response = await self._get_input()
        return PromptResponse(
            content=response.lower().startswith('y'),
            metadata={"raw_response": response}
        )

    async def _handle_json(self, request: PromptRequest) -> PromptResponse:
        """Handle JSON input with optional schema validation"""
        if request.schema:
            print("\nExpected schema:")
            print(json.dumps(request.schema, indent=2))
            print("\nEnter JSON:")

        while True:
            response = await self._get_input()
            try:
                content = json.loads(response)
                # TODO: Add schema validation if request.schema is provided
                return PromptResponse(content=content)
            except json.JSONDecodeError:
                print("Invalid JSON. Please try again:")

    async def _handle_file(self, request: PromptRequest) -> PromptResponse:
        """Handle file reading"""
        print("Enter file path: ", end="")
        filepath = await self._get_input()
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return PromptResponse(
                content=content,
                metadata={"filepath": filepath}
            )
        except Exception as e:
            return PromptResponse(
                content=None,
                error=f"Failed to read file: {str(e)}"
            )

    async def _get_input(self) -> str:
        """Helper method to get input asynchronously"""
        return await asyncio.get_event_loop().run_in_executor(
            None, input
        )

# Example usage
async def main():
    agent = UserConsoleAgent()
    
    # Simple text prompt
    response = await agent.prompt(PromptRequest(
        prompt="What's your name?"
    ))
    print(f"Got response: {response.content}")
    
    # JSON prompt with schema
    response = await agent.prompt(PromptRequest(
        prompt="Please provide user details:",
        type=PromptType.JSON,
        schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        }
    ))
    print(f"Got JSON: {response.content}")
    
    # Confirmation prompt
    response = await agent.prompt(PromptRequest(
        prompt="Do you want to continue?",
        type=PromptType.CONFIRM
    ))
    print(f"User {'agreed' if response.content else 'declined'}")

if __name__ == "__main__":
    asyncio.run(main())
