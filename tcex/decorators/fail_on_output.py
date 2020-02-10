# -*- coding: utf-8 -*-
"""App Decorators Module."""


class FailOnOutput:
    """Fail App if return value (output) value conditions are met.

    This decorator allows for the App to exit on conditions defined in the function
    parameters.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @FailOnOutput(
            arg='fail_on_false', values=['false'], msg='Operation returned a value of "false".'
        )
        def my_method(data):
            return data.lowercase()

    Args:
        fail_enabled (boolean|str, kwargs): Accepts a boolean or string value.  If a boolean value
            is provided that value will control enabling/disabling this feature. A string
            value should reference an item in the args namespace which resolves to a boolean.
            The value of this boolean will control enabling/disabling this feature.
        fail_msg (str, kwargs): The message to log when raising RuntimeError.
        fail_on (list, kwargs): Defaults to None.
            Fail if return value from App method is in the list.
        write_output (bool, kwargs): Defaults to True.
            If true, will call App.write_outputs() before failing on matched fail_on value.
    """

    def __init__(self, **kwargs):
        """Initialize Class properties."""
        self.fail_enabled = kwargs.get('fail_enabled', False)
        self.fail_msg = kwargs.get('fail_msg', f'Method returned invalid output.')
        self.fail_on = kwargs.get('fail_on', [])
        self.write_output = kwargs.get('write_output', True)

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def fail(app, *args, **kwargs):
            """Call the function and store or append return value.

            Args:
                app (class): The instance of the App class "self".
            """
            # call method to get output
            data = fn(app, *args, **kwargs)

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
            if enabled is True:
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
                    if self.write_output and getattr(app, 'write_output'):
                        app.write_output()
                    raise RuntimeError(self.fail_msg)
            return data

        return fail
