class TracerMeta(type):
    def __new__(cls, name, bases, attrs):
        # Create a new class with the same name and bases as the original class
        new_class = super().__new__(cls, name, bases, attrs)
        # Get the type of the first base class
        base_type = bases[0]
        # Iterate over the special methods of the base type
        for attr in dir(base_type):
            if attr.startswith("__") and attr.endswith("__"):
                # Get the original special method
                orig_method = getattr(base_type, attr)
                # Define a new wrapper method that prints some information and
                # calls the original method

                def wrapper(self, *args, **kwargs):
                    print(
                        f"Calling {attr} on {self} with args {args} and kwargs {kwargs}")
                    result = orig_method(self, *args, **kwargs)
                    print(f"Returning {result} from {attr}")
                    # Wrap the result in the same class as self
                    return new_class(result)
                # Set the wrapper method as the new special method of the new
                # class
                setattr(new_class, attr, wrapper)
        # Return the new class
        return new_class



# Import VizTracer
from typing import Sequence
from viztracer import VizTracer
from functools import wraps


# Define the decorator
def viztraced(
    tracer_entries: int = 1000000,
    verbose: int = 1,
    max_stack_depth: int = -1,
    exclude_files: Sequence[str] | None = None,
    include_files: Sequence[str] | None = [
        "./agentsystem",
    ],
    ignore_c_function: bool = False,
    ignore_frozen: bool = False,
    log_func_retval: bool = False,
    log_func_args: bool = False,
    log_print: bool = False,
    log_gc: bool = False,
    log_sparse: bool = False,
    log_async: bool = False,
    log_audit: Sequence[str] | None = None,
    pid_suffix: bool = False,
    file_info: bool = True,
    register_global: bool = True,
    trace_self: bool = False,
    min_duration: float = 0,
    minimize_memory: bool = False,
    dump_raw: bool = False,
    sanitize_function_name: bool = False,
    output_file: str = "result.json",
    **kwargs
):
    # This is a wrapper function that takes the original function as an argument
    def wrapper(func):
        # This is the modified function that will be returned by the decorator
        @wraps(func)
        def inner(*args, **kwargs):
            # Create a VizTracer instance with the given parameters
            with VizTracer(
                tracer_entries=tracer_entries,
                verbose=verbose,
                max_stack_depth=max_stack_depth,
                exclude_files=exclude_files,
                include_files=include_files,
                ignore_c_function=ignore_c_function,
                ignore_frozen=ignore_frozen,
                log_func_retval=log_func_retval,
                log_func_args=log_func_args,
                log_print=log_print,
                log_gc=log_gc,
                log_sparse=log_sparse,
                log_async=log_async,
                log_audit=log_audit,
                pid_suffix=pid_suffix,
                file_info=file_info,
                register_global=register_global,
                trace_self=trace_self,
                min_duration=min_duration,
                minimize_memory=minimize_memory,
                dump_raw=dump_raw,
                sanitize_function_name=sanitize_function_name,
                output_file=output_file,
                **kwargs
            ):
                # Start tracing
                # tracer.start()
                # Call the original function and store the result
                result = func(*args, **kwargs)
            # # Stop tracing
            # tracer.stop()
            # # Save the trace data
            # tracer.save()
            # Return the result of the original function
            return result

        # Return the modified function
        return inner

    # Return the wrapper function
    return wrapper
