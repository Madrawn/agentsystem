from functools import wraps
from types import FunctionType
from typing import (
    Callable,
    Any,
    Dict,
    Optional,
    get_type_hints,
)
import inspect

from agentsystem.models.Response import Response

example_description_open_ai = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current time in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g. San Francisco",
                },
            },
            "required": ["location"],
        },
    },
}


class Tool[T: Any]():
    """Base class for tools that can auto-document themselves from function docstrings."""

    def __init__(
        self,
        func: Optional[Callable[..., T]] = None,
        description: Optional[str] = None,
    ):
        self.func = func
        self._description = (
            description or func and inspect.getdoc(func) or "No description available"
        )
        self._input_type = inspect.signature(func).parameters if func else None

        if func:
            wraps(func)(self)

    def get_openai_description(self) -> Dict[str, Any]:
        """
        Generate an OpenAI-compatible function description from the tool's function.
        """
        if not self.func:
            raise ValueError("No function provided to generate description from")

        # Get function signature
        sig = inspect.signature(self.func)

        # Get type hints
        type_hints = get_type_hints(self.func)

        # Build parameters object
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip self parameter for methods
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name, Any)
            param_info = {
                "type": self._get_json_type(param_type),
                "description": self._get_param_description(param_name),
            }

            # Handle default values
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

            properties[param_name] = param_info

        return {
            "type": "function",
            "function": {
                "name": self.func.__name__,
                "description": self._description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def _get_json_type(self, python_type: type) -> str:
        """Convert Python type to JSON schema type."""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }
        return type_map.get(python_type, "string")

    def _get_param_description(self, param_name: str) -> str:
        """
        Extract parameter description from the function's docstring.
        Returns a default description if none is found.
        """
        if not self.func.__doc__:
            return f"Parameter: {param_name}"

        # Look for parameter description in docstring
        doc_lines = self.func.__doc__.split("\n")
        for i, line in enumerate(doc_lines):
            if param_name in line and ":" in line:
                # Extract description after the colon
                return line.split(":", 1)[1].strip()

        return f"Parameter: {param_name}"

    def __call__(self, *args, **kwargs) -> Response[T]:
        return self.run(*args, **kwargs)

    @property
    def description(self) -> str:
        return self._description
    @classmethod
    def from_function(cls, func) -> "Tool":
        """Create a tool directly from a function, using its docstring as description."""
        return cls(func)

    def run(self, *args, **kwargs) -> Response[T]:
        """Main execution method that handles pre/post processing"""

        def wrapper():
            def resolver(func, *args, **kwargs) -> Callable[..., T]:
                result_function = func(*args, **kwargs)
                return result_function

            resolved_args = resolver(self.execute, *args, **kwargs)()
            return resolved_args

        return Response(wrapper)

    def execute(self, *args, **kwargs) -> Callable[..., T]:
        """Core execution logic - should be overridden by subclasses if not using func"""
        if self.func is None:
            raise NotImplementedError("Either provide a function or override execute()")
        else:
            return lambda: self.func(*args, **kwargs)



# Decorator syntax for instant tool creation
def as_tool[
    T: function
](func: Optional[T] = None, description: Optional[str] = None) -> Tool:
    """
    Decorator to convert a function into a Tool.
    Can be used with or without parameters:

    @as_tool
    def my_func(): ...

    @as_tool(description="Custom description")
    def my_func(): ...
    """

    def decorator(f) -> Tool:
        return Tool(f, description)

    if func is None:
        return decorator  # type: ignore
    return decorator(func)


# Example usage:
@as_tool
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.

    Args:
        n (int): The position in the Fibonacci sequence (0-based)

    Returns:
        int: The nth Fibonacci number

    Example:
        >>> calculate_fibonacci(5)
        8
    """
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


# Alternative way to create tools
def read_file(path: str) -> str:
    """Read and return the contents of a file at the given path.

    Args:
        path (str): Path to the file to read

    Returns:
        str: Contents of the file

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    with open(path, "r") as f:
        return f.read()


file_tool = Tool.from_function(read_file)


# Example showing how to override docstring with custom description
@as_tool(description="Custom description that overrides the docstring")
def custom_described_function():
    """This docstring will be ignored in favor of the custom description."""
    print("Custom described function")


# Example of accessing the documentation
def demonstrate_tool_docs():
    print("Fibonacci tool description:")
    print(calculate_fibonacci.description)
    print(b := calculate_fibonacci(3))
    print("\nFile reader tool description:")
    print(file_tool.description)
    print("\nCustom described tool:")
    print(custom_described_function.description)


if __name__ == "__main__":
    demonstrate_tool_docs()
