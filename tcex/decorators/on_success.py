# -*- coding: utf-8 -*-
"""App Decorators Module."""
# third-party
import wrapt


class OnSuccess:
    """Set exit message on successful execution.

    This decorator will set the supplied msg as the App "exit_message". Typically and App would
    only have 1 exit message so this decorator would typically be used in App that used "actions".

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @OnSuccess(exit_msg='Successfully processed JSON data.')
        def my_method(json_data):
            json.dumps(json_data)

    Args:
        exit_msg (str): The message to send to exit method.
    """

    def __init__(self, exit_msg=None):
        """Initialize Class properties"""
        self.exit_msg = exit_msg or 'App finished successfully.'

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        """Implement __call__ function for decorator.

        Args:
            wrapped (callable): The wrapped function which in turns
                needs to be called by your wrapper function.
            instance (App): The object to which the wrapped
                function was bound when it was called.
            args (list): The list of positional arguments supplied
                when the decorated function was called.
            kwargs (dict): The dictionary of keyword arguments
                supplied when the decorated function was called.

        Returns:
            function: The custom decorator function.
        """

        def completion(app, *args, **kwargs):
            """Call the function and handle any exception.

            Args:
                app (class): The instance of the App class "self".
            """
            app.exit_message = self.exit_msg
            return wrapped(*args, **kwargs)

        return completion(instance, *args, **kwargs)
