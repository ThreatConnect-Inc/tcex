# -*- coding: utf-8 -*-
"""App Decorators Module."""
# third-party
import wrapt


class FailOnOutput:
    """Fail App if return value (output) value conditions are met.

    This decorator allows for the App to exit on conditions defined in the function
    parameters.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @FailOnOutput(
            fail_on=['false'], fail_msg='Operation returned a value of "false".'
        )
        def my_method(data):
            return data.lowercase()

    Args:
        fail_enabled (boolean|str, kwargs): Accepts a boolean or string value.  If a boolean value
            is provided that value will control enabling/disabling this feature. A string
            value should reference an item in the args namespace which resolves to a boolean.
            The value of this boolean will control enabling/disabling this feature.
        fail_msg (str, kwargs): The message to log when raising RuntimeError.
        fail_msg_property (str, kwargs): The App property containting the dynamic exit message.
        fail_on (list, kwargs): Defaults to None.
            Fail if return value from App method is in the list.
        write_output (bool, kwargs): Defaults to True.
            If true, will call App.write_outputs() before failing on matched fail_on value.
    """

    def __init__(self, **kwargs):
        """Initialize Class properties."""
        self.fail_enabled = kwargs.get('fail_enabled', True)
        self.fail_msg = kwargs.get('fail_msg', 'Method returned invalid output.')
        self.fail_on = kwargs.get('fail_on', [])
        self.fail_msg_property = kwargs.get('fail_msg_property')
        self.write_output = kwargs.get('write_output', True)

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

        def fail(app, *args, **kwargs):
            """Call the function and store or append return value.

            Args:
                app (class): The instance of the App class "self".
            """
            # call method to get output
            data = wrapped(*args, **kwargs)

            # self.enable (e.g., True or 'fail_on_false') enables/disables this feature
            enabled = self.fail_enabled
            if not isinstance(self.fail_enabled, bool):
                enabled = getattr(app.args, self.fail_enabled)
                if not isinstance(enabled, bool):  # pragma: no cover
                    raise RuntimeError(
                        'The fail_enabled value must be a boolean or resolved to bool.'
                    )
                app.tcex.log.debug(f'Fail enabled is {enabled} ({self.fail_enabled}).')

            failed = False
            if enabled:
                if isinstance(data, list):
                    # validate each value in the list of results.
                    for d in data:
                        if d in self.fail_on:
                            failed = True
                            break
                else:
                    if data in self.fail_on:
                        failed = True

                if failed:
                    if self.write_output:
                        app.tcex.playbook.write_output()
                        if hasattr(app, 'write_output'):
                            app.write_output()
                    app.exit_message = self.get_fail_msg(app)  # for test cases
                    app.tcex.exit(1, self.get_fail_msg(app))
            return data

        return fail(instance, *args, **kwargs)

    def get_fail_msg(self, app):
        """Return the appropriate fail message."""
        fail_msg = self.fail_msg
        if self.fail_msg_property and hasattr(app, self.fail_msg_property):
            fail_msg = getattr(app, self.fail_msg_property)
        return fail_msg
