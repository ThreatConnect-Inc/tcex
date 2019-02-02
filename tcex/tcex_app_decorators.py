# -*- coding: utf-8 -*-
"""App Decorators"""
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
        """Implement __call__ function for decorator

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
        """Implement __call__ function for decorator

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


class FailOn(object):
    """Fail App if conditions are met.

    This decorator allows for the App to exit on conditions defined in the function
    parameters.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @FailOn(arg='fail_on_false', values=['false'], msg='Operation returned a value of "false".')
        def my_method(data):
            return data.lowercase()
    """

    def __init__(self, arg, values, msg):
        """Initialize Class Properties

        Args:
            arg (str): The args Namespace value that controls whether the App should exit. Arg
                value must be a boolean.
            values (list): The values that, if matched, would trigger an exit.
            msg (str): The message to send to exit method.

        """

        self.arg = arg
        self.msg = msg
        self.values = values

    def __call__(self, fn):
        """Implement __call__ function for decorator

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
            # self.args (e.g., fail_on_false) controls whether the value should be checked).
            if getattr(app.args, self.arg):
                if isinstance(data, list):
                    for d in data:
                        if d in self.values:
                            app.tcex.log.info('{} is enabled.'.format(self.arg))
                            app.tcex.exit(1, self.msg)
                else:
                    if data in self.values:
                        app.tcex.log.info('{} is enabled.'.format(self.arg))
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

    def __init__(self, arg):
        """Initialize Class Properties

        Args:
            arg (str): The arg name from the App which contains the input. This input can be
                a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
                TCEntityArray.
        """

        self.arg = arg

    def __call__(self, fn):
        """Implement __call__ function for decorator

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
            for s in app.tcex.playbook.read(getattr(app.args, self.arg), True):
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
        """Initialize Class Properties

        Args:
            msg (str): The message to send to exit method.
        """

        self.msg = msg

    def __call__(self, fn):
        """Implement __call__ function for decorator

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
        """Initialize Class Properties

        Args:
            msg (str): The message to send to exit method.
        """

        self.msg = msg

    def __call__(self, fn):
        """Implement __call__ function for decorator

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
        """Initialize Class Properties

        Args:
            attribute (str): The name of the App attribute to write data.
        """

        self.attribute = attribute

    def __call__(self, fn):
        """Implement __call__ function for decorator

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

    def __init__(self, arg, array=False):
        """Initialize Class Properties

        Args:
            arg (str): The arg name from the App which contains the input. This input can be
                a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
                TCEntityArray.
        """

        self.array = array
        self.arg = arg

    def __call__(self, fn):
        """Implement __call__ function for decorator

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
                args_list[0] = app.tcex.playbook.read(getattr(app.args, self.arg), self.array)
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
        """Initialize Class Properties

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
        """Implement __call__ function for decorator

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
