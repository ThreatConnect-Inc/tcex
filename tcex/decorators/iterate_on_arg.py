# -*- coding: utf-8 -*-
"""App Decorators Module."""
import inspect


class IterateOnArg:
    """Iterate on values stored in ``self.args`` namespace.

    This decorator will iterate over all value of the supplied arg and return results. This feature
    is helpful when processing a single value (String) or array of values (StringArray). If the App
    was provided the arg ``self.args.colors`` with a value of ``['blue', 'green', 'magenta']``, then
    this decorator would call the function 3 times. Each call to the function would pass one value
    from the array. The return values are stored and returned all at once after the last value is
    processed.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # the args value of "colors" refers to ``self.args.colors``.
        @iterateOnArgs(arg='colors')
        def my_method(colors):
            return colors

        # ** OR **

        # the args value of "colors" refers to ``self.args.colors``.
        @iterateOnArg(arg='colors')
        def my_method(**kwargs):
            return kwargs.get('colors')

    Args:
        arg (str): The arg name from the App which contains the input. This input can be
            a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
            TCEntityArray.
        default (str, kwargs): Defaults to None. Default value to pass to method if arg
            value is None. Only supported for String or StringArray.
        fail_enabled (boolean|str, kwargs): Accepts a boolean or string value.  If a boolean value
            is provided that value will control enabling/disabling this feature. A string
            value should reference an item in the args namespace which resolves to a boolean.
            The value of this boolean will control enabling/disabling this feature.
        fail_msg (str, kwargs): The message to log when raising RuntimeError.
        fail_msg_property (str, kwargs): The App property containting the dynamic exit message.
        fail_on (list, kwargs): Defaults to None. Fail if data read from Redis is in list.
    """

    def __init__(self, arg, **kwargs):
        """Initialize Class properties"""
        self.arg = arg
        self.default = kwargs.get('default')
        self.fail_enabled = kwargs.get('fail_enabled', False)
        self.fail_msg = kwargs.get('fail_msg', f'Invalid value provided for ({arg}).')
        self.fail_msg_property = kwargs.get('fail_msg_property')
        self.fail_on = kwargs.get('fail_on', [])

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def loop(app, *args, **kwargs):
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """
            # get the signature for the decorated method
            fn_signature = inspect.signature(fn).parameters

            # self.enable (e.g., True or 'fail_on_false') enables/disables this feature
            enabled = self.fail_enabled
            if not isinstance(self.fail_enabled, bool):
                enabled = getattr(app.args, self.fail_enabled)
                if not isinstance(enabled, bool):  # pragma: no cover
                    raise RuntimeError(
                        'The fail_enabled value must be a boolean or resolved to bool.'
                    )
            app.tcex.log.debug(f'Fail enabled is {enabled} ({self.fail_enabled}).')

            # retrieve data from Redis if variable and always return and array.
            results = []
            arg_data = app.tcex.playbook.read(getattr(app.args, self.arg))
            arg_type = app.tcex.playbook.variable_type(getattr(app.args, self.arg))
            if arg_data is None:
                arg_data = [None]
            elif not isinstance(arg_data, list):
                arg_data = [arg_data]

            _index = 0
            _array_length = len(arg_data)
            for ad in arg_data:

                # add "magic" args
                if '_index' in fn_signature:
                    kwargs['_index'] = _index
                if '_array_length' in fn_signature:
                    kwargs['_array_length'] = _array_length

                if ad is None and self.default is not None:
                    # set value passed to method to default if value is None.
                    ad = self.default
                    app.tcex.log.debug(
                        f'replacing null value with provided default value "{self.default}".'
                    )

                # check arg_data against fail_on_values
                if enabled and self.fail_on:
                    if ad in self.fail_on:
                        app.tcex.log.debug(f'Invalid value ({ad}) found for {self.arg}.')
                        app.exit_message = self.get_fail_msg(app)  # for test case
                        app.tcex.exit(1, self.get_fail_msg(app))

                # Add logging for debug/troubleshooting
                if (
                    arg_type not in ['Binary', 'BinaryArray']
                    and app.tcex.log.getEffectiveLevel() <= 10
                ):
                    log_string = str(ad)
                    if len(log_string) > 100:  # pragma: no cover
                        log_string = f'{log_string[:100]} ...'
                    app.tcex.log.debug(f'input value: {log_string}')

                # add results to kwargs
                kwargs[self.arg] = ad
                results.append(fn(app, *args, **kwargs))

                # increment index
                _index += 1
            return results

        return loop

    def get_fail_msg(self, app):
        """Return the appropriate fail message."""
        fail_msg = self.fail_msg
        if self.fail_msg_property and hasattr(app, self.fail_msg_property):
            fail_msg = getattr(app, self.fail_msg_property)
        return fail_msg
