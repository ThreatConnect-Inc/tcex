"""App Decorators Module."""
# standard library
from collections.abc import Callable
from typing import Any

# third-party
import wrapt


class Debug:
    """Debug function inputs.

    This decorator will log the inputs to the function to assist in debugging an App.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @Debug()
        def my_method(arg1, args2):
            print(arg1, arg2)
    """

    @wrapt.decorator
    def __call__(self, wrapped: Callable, instance: Callable, args: list, kwargs: dict) -> Any:
        """Implement __call__ function for decorator.

        Args:
            wrapped: The wrapped function which in turns
                needs to be called by your wrapper function.
            instance: The object to which the wrapped
                function was bound when it was called.
            args: The list of positional arguments supplied
                when the decorated function was called.
            kwargs: The dictionary of keyword arguments
                supplied when the decorated function was called.

        Returns:
            function: The custom decorator function.
        """

        def debug(app, *args, **kwargs) -> Any:
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """
            data = wrapped(*args, **kwargs)
            app.tcex.log.debug(
                f'function: "{self.__class__.__name__}", args: "{args}", kwargs: "{kwargs}"'
            )
            return data

        return debug(instance, *args, **kwargs)
