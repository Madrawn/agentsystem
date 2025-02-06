# # import the modules from the package
# import inspect
# import re
# from templates import document_prompt


# def make_functionalist(template):
#     # get the names of the arguments from the template string using regular expressions
#     arg_names = re.findall(r"\{(.*?)\}", template)
#     # create a function that takes a variable number of keyword arguments and formats the template string
#     f = lambda **kwargs: template.format(**kwargs)
#     # set the signature of the function to match the names of the arguments
#     f.__signature__ = inspect.Signature([inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY) for name in arg_names])
#     # return the function
#     return f

# # iterate over the modules in the package
# for module in [document_prompt]:
#     # iterate over the module's variables and their values
#     for name, value in vars(module).items():
#         # check if the value is a string
#         if isinstance(value, str):
#             # convert the string to a function using make_functionalist
#             value = make_functionalist(value)
#             # update the module's variable with the new value
#             setattr(module, name, value)
# print(globals())
# print(locals())
# print(vars(module))