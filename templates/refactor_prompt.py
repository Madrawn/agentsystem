directory_structure_agent = """
Given the following code structure, suggest a proper package layout:
{code}

Return your answer in the following format:
folder1/
    file1.py
    file2.py
folder2/
    file3.py
"""

code_splitter_agent = """
Split the following Python code into separate files based on class definitions.
Ignore import resolution for now.

{code}

For each class, return:
1. The filename it should go in
2. The complete file contents
"""

import_resolver_agent = """
Given the following Python file content and its new location in the package structure,
update all import statements to be correct:

File location: {file_path}
Content: {content}

Return the updated file content with correct import statements.
"""