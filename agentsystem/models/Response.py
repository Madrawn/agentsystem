from typing import Any, Callable


class Response[T:Any]():
    """Creates a response object with the given resolver function. The resolver function generates the response content when called.

        Attributes:
            resolve (Callable[..., str]): A function that generates the response content when called.
            _result (Any): The result of calling the resolver function.
    """
    _result:T = None
    def __init__(self, resolver: Callable[..., T]=lambda: "Empty Response"):
        """Creates a response object with the given resolver function.

        Args:
            resolver (Callable[..., str]): A function that generates the response content when called.
        """
        self._resolve = resolver

    def __call__(self) -> T:
        """Returns the result of calling the resolver function."""
        if self._result is None:
            self._result = self._resolve()
        args:T = self._result
        return args
