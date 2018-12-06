# -*- coding: utf-8 -*-
"""App decorators"""


class PlaybookLoopArg(object):
    """Iterate over Playbook input.

    """
    def __init__(self, input_arg):
        """Initialize Class Properties

        Args:
            input_arg (str): The arg name from the App which contains the input. This input can be
                a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
                TCEntityArray.
        """

        self.input_arg = input_arg

    def __call__(self, fn):
        """[summary]

        Args:
            fn (function): The decorated function.

        Returns:
            function: The custom function for looping.
        """

        def loop(app):
            """Loop over data, calling the decorated method for each value.

            Args:
                app (class): The instance of the App class "self".
            """

            # retrieve data from Redis if variable and always return and array.
            for s in app.tcex.playbook.read(getattr(app.args, self.input_arg), True):
                fn(app, s)  # call decorated function
        return loop
