# -*- coding: utf-8 -*-
"""App Decorators"""


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

        def loop(app, *args):
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """

            # retrieve data from Redis if variable and always return and array.
            for s in app.tcex.playbook.read(getattr(app.args, self.arg), True):
                # update the first item in the tuple
                args_list = list(args)
                try:
                    args_list[0] = s
                except IndexError:
                    args_list.append(s)
                args = tuple(args_list)
                return fn(app, *args)

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

        def exception(app, *args):
            """Call the function and handle any exception.

            Args:
                app (class): The instance of the App class "self".
            """

            try:
                return fn(app, *args)
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

        def completion(app, *args):
            """Call the function and handle any exception.

            Args:
                app (class): The instance of the App class "self".
            """

            app.msg = self.msg
            return fn(app, *args)

        return completion


class Output(object):
    """Set exit message on success"""

    def __init__(self, output, append=False):
        """Initialize Class Properties

        Args:
            output (str): The name of the output variable.
        """

        self.append = append
        self.output = output

    def __call__(self, fn):
        """Implement __call__ function for decorator

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def output(app, *args):
            """Call the function and store or append return value.

            Args:
                app (class): The instance of the App class "self".
            """

            data = fn(app, *args)
            if self.append:
                getattr(app, self.output).append(data)
            else:
                setattr(app, self.output, data)
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

        def read(app, *args):
            """Retrieve/Read data from Redis.

            Args:
                app (class): The instance of the App class "self".
            """

            # retrieve data from Redis and call decorated function
            args_list = list(args)
            try:
                args_list[0] = app.tcex.playbook.read(getattr(app.args, self.arg), self.array)
            except IndexError:
                args_list.append(
                    app.tcex.playbook.read(getattr(app.args, self.arg), self.array)
                )
            args = tuple(args_list)
            return fn(app, *args)

        return read


class WriteOutput(object):
    """Set exit message on success"""

    def __init__(self, var_name, var_type, value=None):
        """Initialize Class Properties

        Args:
            var_name (str): The name of the playbook output variable.
            var_type (str): The type for the playbook output variable.  Supported types are:
                String, Binary, KeyValue, TCEntity, TCEnhancedEntity, StringArray,
                BinaryArray, KeyValueArray, TCEntityArray, TCEnhancedEntityArray.
        """

        self.app_output = 'tc_app_output'  # defined in PlaybookApp class
        self.var_name = var_name
        self.var_type = var_type
        self.value = value

    def __call__(self, fn):
        """Implement __call__ function for decorator

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def output(app, *args):
            """Call the function and store or append return value.

            Args:
                app (class): The instance of the App class "self".
            """

            data = fn(app, *args)
            if self.value is not None:
                app.tcex.playbook.add_output(self.var_name, self.value, self.var_type)
            else:
                app.tcex.playbook.add_output(self.var_name, data, self.var_type)
            return data

        return output
