# -*- coding: utf-8 -*-
"""App Decorators Module."""
# third-party
import wrapt


class Output:
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

    Args:
        attribute (str): The name of the App attribute to write data.
        overwrite (bool): When True and the method is called more than once the previous value
            will be overwritten.
    """

    def __init__(self, attribute, overwrite=False):
        """Initialize Class properties"""
        self.attribute = attribute
        self.overwrite = overwrite

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
            attr = getattr(app, self.attribute)

            # tracker to indicate see if attribute has already been updated
            attr_tracker_name = f'__{self.attribute}_tracker__'
            attr_tracker = False
            try:
                attr_tracker = getattr(app, attr_tracker_name)
            except AttributeError:
                setattr(app, attr_tracker_name, False)

            # update the attribute
            if isinstance(attr, list) and isinstance(data, list) and not self.overwrite:
                attr.extend(data)
            elif isinstance(attr, list) and not self.overwrite:
                attr.append(data)
            elif attr_tracker and isinstance(data, list) and not self.overwrite:
                # convert string to list and extend with data
                d = [attr]
                d.extend(data)
                setattr(app, self.attribute, d)
            elif attr_tracker and not self.overwrite:
                # convert string to list and append with data
                d = [attr]
                d.append(data)
                setattr(app, self.attribute, d)
            else:
                setattr(app, self.attribute, data)

            # update tracker to indicate the attribute has already been set at least once
            setattr(app, attr_tracker_name, True)

            return data

        return output(instance, *args, **kwargs)
