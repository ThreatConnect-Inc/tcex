# -*- coding: utf-8 -*-
"""App Decorators Module."""
import datetime

# import time


class Benchmark(object):
    """Log benchmarking times.

    This decorator will log the time of execution (benchmark_time) to the app.log file. It can be
    helpful in troubleshooting performance issues with Apps.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        import time

        @Debug()
        def my_method():
            time.sleep(1)
    """

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def benchmark(app, *args, **kwargs):
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """

            # before = float('{0:.4f}'.format(time.clock()))
            before = datetime.datetime.now()
            data = fn(app, *args, **kwargs)
            # after = float('{0:.4f}'.format(time.clock()))
            after = datetime.datetime.now()
            app.tcex.log.debug(
                'function: "{}", benchmark_time: "{}"'.format(
                    self.__class__.__name__, after - before
                )
            )
            return data

        return benchmark


class Debug(object):
    """Debug function inputs.

    This decorator will log the inputs to the function to assist in debugging an App.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @Debug()
        def my_method(arg1, args2):
            print(arg1, arg2)
    """

    def __call__(self, fn):
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

            data = fn(app, *args, **kwargs)
            app.tcex.log.debug(
                'function: "{}", args: "{}", kwargs: "{}"'.format(
                    self.__class__.__name__, vars(args), kwargs
                )
            )
            return data

        return debug


class FailOnInput(object):
    """Fail App if input value conditions are met.

    This decorator allows for the App to exit on conditions defined in the function
    parameters.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @FailOnInput(enable=True, values=[None, ''], msg='Invalid input provided.', arg=None)
        def my_method(data):
            return data.lowercase()
    """

    def __init__(self, enable, values, msg, arg=None):
        """Initialize Class Properties.

        Args:
            enable (boolean|str): Accepts a boolean or string value.  If a boolean value is
                provided that value will control enabling/disabling this feature. A string
                value should reference an item in the args namespace which resolves to a boolean.
                The value of this boolean will control enabling/disabling this feature.
            values (list): The values that, if matched, would trigger an exit.
            msg (str): The message to send to exit method.
            arg (str, optional): Defaults to None. The args Namespace value to use for the
                condition. If None the first value passed to the function will be used.
        """
        self.arg = arg
        self.enable = enable
        self.msg = msg
        self.values = values

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

            # self.enable (e.g., True or 'fail_on_false') enables/disables this feature
            if isinstance(self.enable, bool):
                enabled = self.enable
                app.tcex.log.debug('Fail on input is ({}).'.format(self.enable))
            else:
                enabled = getattr(app.args, self.enable)
                app.tcex.log.debug('Fail on input is ({}) for ({}).'.format(enabled, self.enable))
                if not isinstance(enabled, bool):
                    app.tcex.playbook.exit(
                        1, 'The enable value must be a boolean for fail on input.'
                    )

            if enabled is True:
                if self.arg is None:
                    # grab the first arg passed to function to use in condition
                    arg_name = 'input'
                    conditional_value = app.tcex.playbook.read(list(args)[0], embedded=False)
                else:
                    # grab the arg from the args names space to use in condition
                    arg_name = self.arg
                    conditional_value = app.tcex.playbook.read(
                        getattr(app.args, self.arg), embedded=False
                    )

                if conditional_value in self.values:
                    app.tcex.log.error(
                        'Invalid value ({}) provided for ({}).'.format(conditional_value, arg_name)
                    )
                    app.tcex.exit(1, self.msg)

            return fn(app, *args, **kwargs)

        return fail


class FailOnOutput(object):
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
    """

    def __init__(self, enable, values, msg):
        """Initialize Class Properties.

        Args:
            enable (boolean|str): Accepts a boolean or string value.  If a boolean value is
                provided that value will control enabling/disabling this feature. A string
                value should reference an item in the args namespace which resolves to a boolean.
                The value of this boolean will control enabling/disabling this feature.
            values (list): The values that, if matched, would trigger an exit.
            msg (str): The message to send to exit method.

        """
        self.enable = enable
        self.msg = msg
        self.values = values

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
            data = fn(app, *args, **kwargs)
            # self.enable (e.g., True or 'fail_on_false') enables/disables this feature
            if isinstance(self.enable, bool):
                enabled = self.enable
                app.tcex.log.debug('Fail on output is ({}).'.format(self.enable))
            else:
                enabled = getattr(app.args, self.enable)
                app.tcex.log.debug('Fail on output is ({}) for ({}).'.format(enabled, self.enable))
                if not isinstance(enabled, bool):
                    app.tcex.playbook.exit(
                        1, 'The enable value must be a boolean for fail on output.'
                    )

            failed = False
            if enabled is True:
                if isinstance(data, list):
                    # validate each value in the list of results.
                    for d in data:
                        if d in self.values:
                            failed = True
                else:
                    if data in self.values:
                        failed = True

                if failed:
                    app.tcex.exit(1, self.msg)
            return data

        return fail


class IterateOnArg(object):
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
        def my_method(value):
            return value
    """

    def __init__(self, arg, default=None, fail_on=None):
        """Initialize Class Properties.

        Args:
            arg (str): The arg name from the App which contains the input. This input can be
                a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
                TCEntityArray.
            default (str, optional): Defaults to None. Default value to pass to method if arg
                value is None. Only supported for String or StringArray.
            fail_on (list, optional): Defaults to None. Fail if data read from Redis is in list.
        """
        self.arg = arg
        self.default = default
        self.fail_on = fail_on

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

            # retrieve data from Redis if variable and always return and array.
            r = []
            arg_data = app.tcex.playbook.read(getattr(app.args, self.arg))
            arg_type = app.tcex.playbook.variable_type(getattr(app.args, self.arg))
            if not isinstance(arg_data, list):
                arg_data = [arg_data]

            if not arg_data:
                app.tcex.exit(1, 'No data retrieved for arg ({}).'.format(self.arg))

            for s in arg_data:
                if s is None and self.default is not None:
                    # set value passed to method to default if value is None.
                    s = self.default
                    app.tcex.log.debug(
                        'a null input was provided, using default value "{}" instead.'.format(s)
                    )

                if self.fail_on is not None:
                    if s in self.fail_on:
                        app.tcex.playbook.exit(
                            1,
                            'Arg value for IterateOnArg matched fail_on value ({}).'.format(
                                self.fail_on
                            ),
                        )

                # Add logging for debug/troubleshooting
                if (
                    arg_type not in ['Binary', 'BinaryArray']
                    and app.tcex.log.getEffectiveLevel() == 10
                ):
                    log_string = str(s)
                    if len(log_string) > 100:
                        log_string = '{} ...'.format(log_string[:100])
                    app.tcex.log.debug('input value: {}'.format(log_string))

                # update the first item in the tuple
                args_list = list(args)
                try:
                    args_list[0] = s
                except IndexError:
                    args_list.append(s)
                args = tuple(args_list)
                r.append(fn(app, *args, **kwargs))
            return r

        return loop


class OnException(object):
    """Set exit message on failed execution.

    This decorator will catch the generic "Exception" error, log the supplied error message, set
    the "exit_message", and exit the App with an exit code of 1.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @OnException(msg='Failed to process JSON data.')
        def my_method(json_data):
            json.dumps(json_data)
    """

    def __init__(self, msg=None):
        """Initialize Class Properties.

        Args:
            msg (str): The message to send to exit method.
        """
        self.msg = msg

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def exception(app, *args, **kwargs):
            """Call the function and handle any exception.

            Args:
                app (class): The instance of the App class "self".
            """

            try:
                return fn(app, *args, **kwargs)
            except Exception as e:
                app.tcex.log.error('method failure ({})'.format(e))
                app.tcex.exit(1, self.msg)

        return exception


class OnSuccess(object):
    """Set exit message on successful execution.

    This decorator will set the supplied msg as the App "exit_message". Typically and App would
    only have 1 exit message so this decorator would typically be used in App that used "actions".

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @OnSuccess(msg='Successfully processed JSON data.')
        def my_method(json_data):
            json.dumps(json_data)
    """

    def __init__(self, msg=None):
        """Initialize Class Properties.

        Args:
            msg (str): The message to send to exit method.
        """

        self.msg = msg

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
            app.exit_message = self.msg
            return fn(app, *args, **kwargs)

        return completion


class Output(object):
    """Store the method return value in self.<attribute>.

    This decorator will write, append, or extend the methods return value to the App attribute
    provided in the ``attribute`` input. The ``attribute`` must first be defined in the
    ``__init__()`` method of the App before the decorator is used.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        def __init__(self, _tcex):
            super(App, self).__init__(_tcex)
            self.output_strings = []  # Output decorator writes here.

        @Output(attribute='output_strings')
        def my_method(data):
            return data.lowercase()
    """

    def __init__(self, attribute):
        """Initialize Class Properties.

        Args:
            attribute (str): The name of the App attribute to write data.
        """

        self.attribute = attribute

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def output(app, *args, **kwargs):
            """Call the function and store or append return value.

            Args:
                app (class): The instance of the App class "self".
            """
            data = fn(app, *args, **kwargs)
            attr = getattr(app, self.attribute)
            if isinstance(data, list) and isinstance(attr, list):
                getattr(app, self.attribute).extend(data)
            elif isinstance(attr, list):
                getattr(app, self.attribute).append(data)
            else:
                setattr(app, self.attribute, data)
            return data

        return output


class ReadArg(object):
    """Read value of App arg resolving any playbook variables.

    This decorator will read the args from Redis, if it is a playbook variable, and pass the
    resolved value to the function.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @ReadArg(arg='color')
        def my_method(color):
            print('color', color)
    """

    def __init__(self, arg, array=False, default=None, fail_on=None):
        """Initialize Class Properties.

        Args:
            arg (str): The arg name from the App which contains the input. This input can be
                a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
                TCEntityArray.
            array (bool, optional): Defaults to False. If True the arg value will always be
                returned as an array.
            default (str, optional): Defaults to None. Default value to pass to method if arg
                value is None. Only supported for String or StringArray.
            fail_on (list, optional): Defaults to None. Fail if data read from Redis is in list.
        """
        self.arg = arg
        self.array = array
        self.default = default
        self.fail_on = fail_on

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def read(app, *args, **kwargs):
            """Retrieve/Read data from Redis.

            Args:
                app (class): The instance of the App class "self".
            """
            # retrieve data from Redis and call decorated function
            args_list = list(args)
            try:
                arg_data = app.tcex.playbook.read(getattr(app.args, self.arg), self.array)
                arg_type = app.tcex.playbook.variable_type(getattr(app.args, self.arg))
                if self.default is not None and arg_data is None:
                    arg_data = self.default
                if self.fail_on is not None:
                    if arg_data in self.fail_on:
                        app.tcex.playbook.exit(
                            1,
                            'Arg value for ReadArg matched fail_on value ({}).'.format(
                                self.fail_on
                            ),
                        )
                args_list[0] = arg_data

                # Add logging for debug/troubleshooting
                if (
                    arg_type not in ['Binary', 'BinaryArray']
                    and app.tcex.log.getEffectiveLevel() == 10
                ):
                    log_string = str(arg_data)
                    if len(log_string) > 100:
                        log_string = '{} ...'.format(log_string[:100])
                    app.tcex.log.debug('input value: {}'.format(log_string))
            except IndexError:
                args_list.append(app.tcex.playbook.read(getattr(app.args, self.arg), self.array))
            args = tuple(args_list)

            return fn(app, *args, **kwargs)

        return read


class WriteOutput(object):
    """Write the App output variables to Redis.

    This decorator will take the functions return value and write the data to Redis using the
    key and variable_type. An optional hard coded value can be passed, which will override the
    return value. If multiple value are provided for the same output variable there is an option
    to overwrite the previous value.

    This decorator is intended for very simple Apps. Using the `write_output()` method of the App
    template is the recommended way of writing output data.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @WriteOutput(key='color', variable_type='String')
        def my_method(color):
            return color.lowercase()
    """

    def __init__(self, key, variable_type, value=None, overwrite=True):
        """Initialize Class Properties.

        Args:
            key (str): The name of the playbook output variable.
            variable_type (str): The type for the playbook output variable.  Supported types are:
                String, Binary, KeyValue, TCEntity, TCEnhancedEntity, StringArray,
                BinaryArray, KeyValueArray, TCEntityArray, TCEnhancedEntityArray.
            value (str): When a value is provided that value will be written instead of the data
                returned from the function call.
            overwrite (bool): When True and more than one value is provided for the same variable
                the previous value will be overwritten.
        """
        self.key = key
        self.overwrite = overwrite
        self.value = value
        self.variable_type = variable_type

    def __call__(self, fn):
        """Implement __call__ function for decorator.

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def output(app, *args, **kwargs):
            """Call the function and store or append return value.

            Args:
                app (class): The instance of the App class "self".
            """
            data = fn(app, *args, **kwargs)
            index = '{}-{}'.format(self.key, self.variable_type)
            if self.value is not None:
                # store user provided data
                app.tcex.playbook.add_output(self.key, self.value, self.variable_type)
            elif app.tcex.playbook.output_data.get(index) and not self.overwrite:
                # skip data since a previous value has already been written
                pass
            else:
                # store data returned by function call
                app.tcex.playbook.add_output(self.key, data, self.variable_type)
            return data

        return output
