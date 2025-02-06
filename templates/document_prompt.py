import inspect
import re


default_sys = """This is a prompt for a language model to help me write a document. The document content is enclosed between <<START:FILE_CONTENT>> and <<END:FILE_CONTENT>> tags. Each line of the document is prefixed with a line number. The user prompt is after the document content. The model should reference the location in the document by using "@<line number>: ..." notation."""
default_prompt = """
<<START:FILE_CONTENT>>
{file_content}
<<END:FILE_CONTENT>>
{user_prompt}
"""

def make_functionalist(template):
    # get the names of the arguments from the template string using regular expressions
    arg_names = re.findall(r"\{(.*?)\}", template)
    # create a function that takes a variable number of keyword arguments and formats the template string
    f = lambda **kwargs: template.format(**kwargs)
    # set the signature of the function to match the names of the arguments
    f.__signature__ = inspect.Signature([inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY) for name in arg_names])
    # return the function
    return f

# iterate over the module's variables and their values
for name, value in list(vars().items()):
    # check if the value is a string
    if isinstance(value, str):
        # convert the string to a function using make_functionalist
        value = make_functionalist(value)
        # update the module's variable with the new value
        globals()[name] = value