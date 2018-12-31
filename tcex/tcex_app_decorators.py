# -*- coding: utf-8 -*-
"""App Decorators"""
import datetime

# import time


class Benchmark(object):
    """Benchmark a function"""

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
    """Debug a function"""

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


class InterateOnArg(object):
    """Iterate over arg data"""

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
    """Handle Exception in function"""

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
    """Set exit message on successful execution"""

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

            app.msg = self.msg
            return fn(app, *args, **kwargs)

        return completion


class Output(object):
    """Set exit message on success"""

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
    """Retrieve value from Redis for arg that is a playbook variables."""

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
    """Set exit message on success"""

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
            elif app.tcex.playbook.output_data.get(index) and not overwrite:
                # skip data since a previous value has already been written
                pass
            else:
                # store data returned by function call
                app.tcex.playbook.add_output(self.key, data, self.variable_type)
            return data

        return output
