# -*- coding: utf-8 -*-
"""App Decorators Module."""


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
        exit_msg_property (str, kwargs): The App property containting the dynamic exit message.
    """

    def __init__(self, exit_msg=None, exit_msg_property=None):
        """Initialize Class properties"""
        self.exit_msg = exit_msg or 'App finished successfully.'
        self.exit_msg_property = exit_msg_property

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def completion(app, *args, **kwargs):
            """Call the function and handle any exception.

            Args:
                app (class): The instance of the App class "self".
            """
            app.exit_message = self.get_exit_msg(app)
            return fn(app, *args, **kwargs)

        return completion

    def get_exit_msg(self, app):
        """Return the appropriate fail message."""
        exit_msg = self.exit_msg
        if self.exit_msg_property and hasattr(app, self.exit_msg_property):
            exit_msg = getattr(app, self.exit_msg_property)
        return exit_msg
