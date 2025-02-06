import ast
from pathlib import Path


def get_matched_files_content(base_dir, pattern):
    """Returns the content of all files in base_dir that match pattern as a single string with each file's content separated by triple backticks.

    Args:
        base_dir (Path): The directory to search for matching files.
        pattern (str): A glob-style path pattern to use for searching for files.

    Returns:
        str: The content of all matched files separated by triple backticks.
    Usage example:
    ```python
    base_dir = "/path/to/base/directory"
    pattern = "**/*.py"  # or any other pattern you want to use
    content = get_matched_files_content(base_dir, pattern)
    print(content)
    ```
    """
    files = get_matched_files(base_dir, pattern)
    content = ""
    for file in files:
        with open(file, 'r') as f:
            content += f"{file}\n```\n{f.read()}\n```\n\n"
    return content


def get_matched_files(base_dir, pattern):
    files = Path(base_dir).glob(pattern)
    return files


class ClassExtractor(ast.NodeVisitor):
    def __init__(self):
        self.classes = []

    def visit_ClassDef(self, node):
        # Get the class name
        name = node.name
        # Get the class docstring
        docstring = ast.get_docstring(node)
        # Get the class attributes and methods
        attributes = []
        methods = []
        for statement in node.body:
            if isinstance(statement, ast.Assign):
                # Get the attribute name and value
                attr_name = statement.targets[0].id
                attr_value = statement.value
                attributes.append((attr_name, attr_value))
            elif isinstance(statement, ast.FunctionDef):
                # Get the method name and docstring
                method_name = statement.name
                method_docstring = ast.get_docstring(statement)
                methods.append((method_name, method_docstring))
        # Store the class information
        self.classes.append((name, docstring, attributes, methods))
        # Continue visiting the child nodes
        self.generic_visit(node)


#question = "What is the purpose of this class? How could it be improved or extended?"


def python_code_prompt_gen(file, question):
    # Parse the source code
    extractor = extract_ast(file)

    # Print the extracted classes and their docstrings
    # for name, docstring, attributes, methods in extractor.classes:
    #     print(f"Class: {name}")
    #     print(f"Docstring: {docstring}")
    #     print(f"Attributes: {attributes}")
    #     print(f"Methods: {methods}")
    #     print()

    # Create a prompt for the language model
    prompts = list(prompt_from_source(extractor, question))

    # Print the prompt
    return prompts

def extract_ast(file):
    source = open(file).read()
    tree = ast.parse(source)

    # Create an instance of the class extractor
    extractor = ClassExtractor()

    # Visit the tree
    extractor.visit(tree)
    return extractor, tree


def prompt_from_source(extractor, question):
    for name, docstring, attributes, methods in extractor.classes:
        prompt = ""
        # Format the class information as a markdown text
        prompt += f"## Class: {name}\n"
        prompt += f"**Docstring:** <docstring>{docstring}</docstring>\n"
        prompt += "**Attributes:**\n"
        for attr_name, attr_value in attributes:
            prompt += f"- `{attr_name}`: {attr_value}\n"
        prompt += "**Methods:**\n"
        for method_name, method_docstring in methods:
            prompt += f"- `{method_name}`: <docstring>{method_docstring}</docstring>\n"
        # Append a question or a task for the model
        prompt += f"\n**Question:** {question}\n"
        yield prompt
