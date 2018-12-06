# -*- coding: utf-8 -*-
"""App Decorators"""


class AppendOutput(object):
    """Set exit message on success

    """

    def __init__(self, output_list):
        """Initialize Class Properties

        Args:
            output (str): The name of the output variable.
        """

        self.output_list = output_list

    def __call__(self, fn):
        """Implement __call__ function for decorator

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def append(app, *args):
            """Call the function and append return value.

            Args:
                app (class): The instance of the App class "self".
            """

            output = getattr(app, self.output_list)
            output.append(fn(app, args))

        return append


class InterateOnArg(object):
    """Iterate over arg data"""

    def __init__(self, input_arg):
        """Initialize Class Properties

        Args:
            input_arg (str): The arg name from the App which contains the input. This input can be
                a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
                TCEntityArray.
        """

        self.input_arg = input_arg

    def __call__(self, fn):
        """Implement __call__ function for decorator

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def loop(app):
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """

            # retrieve data from Redis if variable and always return and array.
            for s in app.tcex.playbook.read(getattr(app.args, self.input_arg), True):
                fn(app, s)  # call decorated function

        return loop


class OnException(object):
    """Handle Exception in function"""

    def __init__(self, exit_message=None):
        """Initialize Class Properties

        Args:
            exit_message (str): The message to send to exit method.
        """

        self.exit_message = exit_message

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
                fn(app, args)
            except Exception as e:
                app.tcex.log.error('method failure ({})'.format(e))
                app.tcex.exit(1, self.exit_message)

        return exception


class OnSuccess(object):
    """Set exit message on successful execution"""

    def __init__(self, exit_message=None):
        """Initialize Class Properties

        Args:
            exit_message (str): The message to send to exit method.
        """

        self.exit_message = exit_message

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

            app.exit_message = self.exit_message

        return completion


class Output(object):
    """Set function output"""

    def __init__(self, output):
        """Initialize Class Properties

        Args:
            output (str): The name of the output variable.
        """

        self.output = output

    def __call__(self, fn):
        """Implement __call__ function for decorator

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def append(app, *args):
            """Call the function and store the output.

            Args:
                app (class): The instance of the App class "self".
            """

            setattr(app, self.output, fn(app, args))

        return append


class ReadArg(object):
    """Retrieve value from Redis for args that are variables."""

    def __init__(self, input_arg, array=False):
        """Initialize Class Properties

        Args:
            input_arg (str): The arg name from the App which contains the input. This input can be
                a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
                TCEntityArray.
        """

        self.array = array
        self.input_arg = input_arg

    def __call__(self, fn):
        """Implement __call__ function for decorator

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom decorator function.
        """

        def read(app):
            """Retrieve/Read data from Redis.

            Args:
                app (class): The instance of the App class "self".
            """

            # retrieve data from Redis and call decorated function
            fn(app, app.tcex.playbook.read(getattr(app.args, self.input_arg), self.array))

        return read
