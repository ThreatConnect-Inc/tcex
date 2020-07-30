# -*- coding: utf-8 -*-
"""App Decorators Module."""
# third-party
import wrapt


class WriteOutput:
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

    Args:
        key (str): The name of the playbook output variable.
        variable_type (str): The type for the playbook output variable.  Supported types are:
            String, Binary, KeyValue, TCEntity, TCEnhancedEntity, StringArray,
            BinaryArray, KeyValueArray, TCEntityArray, TCEnhancedEntityArray.
        default (str): If the method return is None use the provided value as a default.
        overwrite (bool): When True and more than one value is provided for the same variable
            the previous value will be overwritten.
    """

    def __init__(self, key, variable_type, default=None, overwrite=True):
        """Initialize Class properties"""
        self.key = key
        self.overwrite = overwrite
        self.default = default
        self.variable_type = variable_type

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

        def output(app, *args, **kwargs):
            """Call the function and store or append return value.

            Args:
                app (class): The instance of the App class "self".
            """
            data = wrapped(*args, **kwargs)
            if data is None and self.default is not None:
                data = self.default

            index = f'{self.key}-{self.variable_type}'
            if app.tcex.playbook.output_data.get(index) and not self.overwrite:
                # skip data since a previous value has already been written
                pass
            else:
                # store data returned by function call or default
                app.tcex.playbook.add_output(self.key, data, self.variable_type)
            return data

        return output(instance, *args, **kwargs)
