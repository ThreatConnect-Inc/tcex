"""App Decorators Module."""
# standard library
import inspect
from typing import List, Union

# third-party
import wrapt

# first-party
from tcex.validators import (
    ValidationError,
    equal_to,
    greater_than,
    greater_than_or_equal,
    in_range,
    less_than,
    less_than_or_equal,
    not_in,
    to_bool,
    to_float,
    to_int,
)


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
        fail_on (list, kwargs): Defaults to None. Fail if data read from Redis is in list.
    """

    def __init__(self, arg, **kwargs):
        """Initialize Class properties"""
        self.arg = arg
        self.default = kwargs.get('default')
        self.fail_enabled = kwargs.get('fail_enabled', False)
        self.fail_msg = kwargs.get('fail_msg')
        self.fail_on = kwargs.get('fail_on', [])
        self.transforms: Union[List[callable], callable] = kwargs.get('transforms', [])
        self.validators: Union[List[callable], callable] = kwargs.get('validators', [])
        if self.fail_on:
            self.validators.insert(0, not_in(self.fail_on))

        self._init_validators(**kwargs)

    def _init_validators(self, **kwargs):
        validators_map = {
            'in_range': in_range,
            'equal_to': equal_to,
            'less_than': less_than,
            'less_than_or_equal': less_than_or_equal,
            'greater_than': greater_than,
            'greater_than_or_equal': greater_than_or_equal,
        }

        for k, v in filter(lambda item: item[0] in validators_map, kwargs.items()):
            validator = validators_map.get(k)
            if isinstance(v, list):
                self.validators.append(validator(*v))
            elif isinstance(v, dict):
                self.validators.append(validator(**v))
            else:
                self.validators.append(validator(v))

        transform_map = {
            'to_int': to_int,
            'to_float': to_float,
            'to_bool': to_bool,
        }

        for transform_name in filter(lambda t: t in transform_map, kwargs.keys()):
            transform = transform_map.get(transform_name)
            transform_args = kwargs.get(transform_name)
            if isinstance(transform_args, list):
                self.transforms.append(transform(*transform_args))
            elif isinstance(transform_args, dict):
                self.transforms.append(transform(**transform_args))
            else:
                self.transforms.append(transform())

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

        def loop(app, *args, **kwargs):
            """Iterate over data, calling the decorated function for each value.

            Args:
                app (class): The instance of the App class "self".
            """
            # retrieve the label for the current Arg
            label = app.tcex.ij.params_dict.get(self.arg, {}).get('label')

            # get the signature for the decorated method
            fn_signature = inspect.signature(wrapped, follow_wrapped=True).parameters

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

                try:
                    for transform in self.transforms:
                        ad = transform(ad, self.arg, label)
                except ValidationError as v:
                    value_formatted = f'"{ad}"' if isinstance(ad, str) else str(ad)
                    message = f'Invalid value ({value_formatted}) found for "{label}": {v.message}'
                    app.tcex.log.error(message)
                    if self.fail_msg:
                        app.exit_message = self.fail_msg  # for test cases
                        app.tcex.exit(1, self.fail_msg)
                    else:
                        app.exit_message = message
                        app.tcex.exit(1, message)

                # check ad against fail_on_values
                if enabled:
                    try:
                        # pylint: disable=consider-using-generator
                        list([v(ad, self.arg, label) for v in self.validators])
                    except ValidationError as v:
                        value_formatted = f'"{ad}"' if isinstance(ad, str) else str(ad)
                        message = (
                            f'Invalid value ({value_formatted}) found for "{label}": {v.message}'
                        )
                        app.tcex.log.error(message)
                        if self.fail_msg:
                            app.exit_message = self.fail_msg  # for test cases
                            app.tcex.exit(1, self.fail_msg)
                        else:
                            app.exit_message = message
                            app.tcex.exit(1, message)

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
                results.append(wrapped(*args, **kwargs))

                # increment index
                _index += 1
            return results

        return loop(instance, *args, **kwargs)
