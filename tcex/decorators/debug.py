# -*- coding: utf-8 -*-
"""App Decorators Module."""
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
    def __call__(self, wrapped, instance, args, kwargs):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def debug(app, *args, **kwargs):
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
