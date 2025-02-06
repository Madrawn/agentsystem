import pytest
from src.agentsystem.agents.tools.tool import Tool

def test_execute_simple_function():
    def simple_function():
        return "simple result"
    
    tool = Tool(simple_function)
    assert tool.execute()() == "simple result"

def test_execute_function_with_args():
    def function_with_args(a, b):
        return a + b
    
    tool = Tool(function_with_args)
    assert tool.execute(2, 3)() == 5

def test_execute_function_with_kwargs():
    def function_with_kwargs(a, b=10):
        return a + b
    
    tool = Tool(function_with_kwargs)
    assert tool.execute(5, b=5)() == 10

def test_execute_function_raises_exception():
    def function_raises_exception():
        raise ValueError("An error occurred")
    
    tool = Tool(function_raises_exception)
    with pytest.raises(ValueError, match="An error occurred"):
        tool.execute()()

def test_execute_function_returns_complex_data():
    def function_returns_complex_data():
        return {"key": "value", "list": [1, 2, 3]}
    
    tool = Tool(function_returns_complex_data)
    result = tool.execute()()
    assert result == {"key": "value", "list": [1, 2, 3]}
    def test_get_openai_description_simple_function():
        def simple_function():
            """Simple function description."""
            pass
        
        tool = Tool(simple_function)
        description = tool.get_openai_description()
        
        expected_description = {
            "type": "function",
            "function": {
                "name": "simple_function",
                "description": "Simple function description.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        assert description == expected_description

def test_get_openai_description_with_args():
    def function_with_args(a: int, b: str):
        """Function with args description."""
        pass
    
    tool = Tool(function_with_args)
    description = tool.get_openai_description()
    
    expected_description = {
        "type": "function",
        "function": {
            "name": "function_with_args",
            "description": "Function with args description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "Parameter: a"
                    },
                    "b": {
                        "type": "string",
                        "description": "Parameter: b"
                    }
                },
                "required": ["a", "b"]
            }
        }
    }
    
    assert description == expected_description

def test_get_openai_description_with_default_args():
    def function_with_default_args(a: int, b: str = "default"):
        """Function with default args description."""
        pass
    
    tool = Tool(function_with_default_args)
    description = tool.get_openai_description()
    
    expected_description = {
        "type": "function",
        "function": {
            "name": "function_with_default_args",
            "description": "Function with default args description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "Parameter: a"
                    },
                    "b": {
                        "type": "string",
                        "description": "Parameter: b"
                    }
                },
                "required": ["a"]
            }
        }
    }
    
    assert description == expected_description

def test_get_openai_description_no_function():
    tool = Tool()
    with pytest.raises(ValueError, match="No function provided to generate description from"):
        tool.get_openai_description()
