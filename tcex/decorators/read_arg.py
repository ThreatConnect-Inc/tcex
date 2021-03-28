"""ReadArg App Decorators."""
# standard library
from typing import Callable, List, Union

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


class ReadArg:
    """Read value of App arg resolving any playbook variables.

    This decorator will read the args from Redis, if it is a playbook variable, and pass the
    resolved value to the function.

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        @ReadArg(arg='color', default='red')
        @ReadArg(arg='number')
        @ReadArg(
            arg='fruits',
            array=True,
            fail_on=[None, []],
            fail_enabled=True
        )
        def my_method(self, color, number, fruits):
            print('color', color)
            print('number', number)
            print('fruit', fruit)

        # ** OR **

        @ReadArg(arg='color', default='red')
        @ReadArg(arg='number')
        @ReadArg(
            arg='fruits',
            array=True,
            fail_on=[None, []],
            fail_enabled=True
        )
        def my_method(self, **kwargs):
            print('color', kwargs.get('color'))
            print('number', kwargs.get('number')
            print('fruit', kwargs.get('fruit')

    Args:
        arg (str): The arg name from the App which contains the input. This input can be
            a Binary, BinaryArray, KeyValue, KeyValueArray, String, StringArray, TCEntity, or
            TCEntityArray.
        array (bool, kwargs): Defaults to False. If True the arg value will always be
            returned as an array.
        default (str, kwargs): Defaults to None. Default value to pass to method if arg
            value is None. Only supported for String or StringArray.
        equal_to (Union[Any, List[Any], Dict[str, Any], kwargs):  Verifies that the arg value is
            equal to the given compare_to value.
        fail_enabled (boolean|str, kwargs): Accepts a boolean or string value.  If a boolean value
            is provided that value will control enabling/disabling this feature. A string
            value should reference an item in the args namespace which resolves to a boolean.
            The value of this boolean will control enabling/disabling this feature.
        fail_on (list, kwargs): Defaults to None. Fail if data read from Redis is in list.
        greater_than (Union[Any, List[Any], Dict[str, Any], kwargs):  Verifies that the arg value is
            greater than the given compare_to value.
        greater_than_or_equal (Union[Any, List[Any], Dict[str, Any], kwargs):  Verifies that the arg
            value is greater than or equal to the given compare_to value.
        group_values (bool, kwargs): Defaults to False. If True, return a list of group names from
            the given argument.
        group_ids (bool, kwargs): Defaults to False. If True, return a list of group ids from the
            given argument.
        in_range (Dict[str, float]|List[float], kwargs): Validator that verifies the arg value is in
            the range min <= value <= max.  For Array args, will verify each member of the array.
            Expected value is {'min': <min_value>, 'max': <max_value>} OR [<min_value>, <max_value>]
        indicator_values (bool, kwargs): Defaults to False. If True, return a list of
            indicator values from the given argument (e.g. ["foo.example.com", "bar.example.com"]).
        less_than (Union[Any, List[Any], Dict[str, Any], kwargs):  Verifies that the arg value is
            less than the given compare_to value.
        less_than_or_equal (Union[Any, List[Any], Dict[str, Any], kwargs):  Verifies that the arg
            value is less than or equal to the given compare_to value.
        strip_values (bool, kwargs): Defaults to False.  If True, automatically strips whitespace
            from arg value.  Not valid if group_values, group_ids, or indicator_values is True.
        to_bool (bool, kwargs): Transform the arg value into a bool where 'true' (case-insensitive),
            '1' (str), and 1 (int or float) will become True and everything else will become False.
            Accepts one parameter 'allow_none' which, if True, will succeed if the arg value is
            none.
        to_float (bool, kwargs):  Transform the arg value into an float.  Accepts one
            parameter 'allow_none' which, if True, will succeed if the arg value is none.
        to_int (bool, kwargs):  Transform the arg value into an int.  Accepts one
            parameter 'allow_none' which, if True, will succeed if the arg value is none.
        validators (Union[List[Callable], Callable]): A callable or list of callables that will be
            invoked with the arg value and arg name and must raise a ValidationError if
            the arg is not valid.  Any return value will be ignored.  Validators will be invoked in
            the order they are given.  If one validator fails, no others will be invoked.
    """

    def __init__(self, arg, **kwargs):
        """Initialize Class properties"""
        self.arg = arg
        self.array = kwargs.get('array')
        self.default = kwargs.get('default')
        self.fail_enabled = kwargs.get('fail_enabled', True)
        self.fail_msg = kwargs.get('fail_msg')
        self.fail_on = kwargs.get('fail_on', [])
        self.embedded = kwargs.get('embedded', True)
        self.indicator_values = kwargs.get('indicator_values', False)
        self.group_values = kwargs.get('group_values', False)
        self.group_ids = kwargs.get('group_ids', False)
        self.strip_values = kwargs.get('strip_values', False)
        self.transforms: Union[List[Callable], Callable] = kwargs.get('transforms', [])
        self.validators: Union[List[Callable], Callable] = kwargs.get('validators', [])
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

        def read(app, *args, **kwargs):
            """Retrieve/Read data from Redis.

            Args:
                app (class): The instance of the App class "self".
            """
            # retrieve the label for the current Arg
            label = app.tcex.ij.params_dict.get(self.arg, {}).get('label')

            # self.enable (e.g., True or 'fail_on_false') enables/disables this feature
            enabled = self.fail_enabled
            if not isinstance(self.fail_enabled, bool):
                enabled = getattr(app.args, self.fail_enabled)
                if not isinstance(enabled, bool):  # pragma: no cover
                    raise RuntimeError(
                        'The fail_enabled value must be a boolean or resolved to bool.'
                    )
                app.tcex.log.debug(f'Fail enabled is {enabled} ({self.fail_enabled}).')

            try:
                # read arg from namespace
                arg = getattr(app.args, self.arg)
            except AttributeError:
                if enabled:
                    app.tcex.log.error(f'Arg {self.arg} was not found in Arg namespace.')
                    message = self.fail_msg or f'Invalid value provided for "{label}" ({self.arg}).'
                    app.exit_message = message  # for test cases
                    app.tcex.exit(1, message)
                else:
                    # add results to kwargs
                    kwargs[self.arg] = self.default
                    return wrapped(*args, **kwargs)

            # retrieve data from Redis and call decorated function
            if self.indicator_values:
                arg_data = app.tcex.playbook.read_indicator_values(arg)
            elif self.group_values:
                arg_data = app.tcex.playbook.read_group_values(arg)
            elif self.group_ids:
                arg_data = app.tcex.playbook.read_group_ids(arg)
            else:
                arg_data = app.tcex.playbook.read(arg, self.array, embedded=self.embedded)
                if self.strip_values and arg_data is not None:
                    variable_type = app.tcex.playbook.variable_type(arg)
                    if variable_type == 'String':
                        arg_data = arg_data.strip()
                    elif variable_type == 'StringArray':
                        arg_data = [s.strip() for s in arg_data]
                    else:
                        app.tcex.log.warn(
                            f'strip_values is enabled but variable is of type {variable_type}, '
                            'only String and StringArray variables can be stripped.'
                        )

            if self.default is not None and arg_data is None:
                arg_data = self.default
                app.tcex.log.debug(
                    f'replacing null value with provided default value "{self.default}".'
                )

            try:
                for transform in self.transforms:
                    arg_data = transform(arg_data, self.arg, label)
            except ValidationError as v:
                value_formatted = f'"{arg_data}"' if isinstance(arg_data, str) else str(arg_data)
                message = f'Invalid value ({value_formatted}) found for "{label}": {v.message}'
                app.tcex.log.error(message)
                if self.fail_msg:
                    app.exit_message = self.fail_msg  # for test cases
                    app.tcex.exit(1, self.fail_msg)
                else:
                    app.exit_message = message
                    app.tcex.exit(1, message)

            # check arg_data against fail_on_values
            if enabled:
                try:
                    # pylint: disable=consider-using-generator
                    list([v(arg_data, self.arg, label) for v in self.validators])
                except ValidationError as v:
                    value_formatted = (
                        f'"{arg_data}"' if isinstance(arg_data, str) else str(arg_data)
                    )
                    message = f'Invalid value ({value_formatted}) found for "{label}": {v.message}'
                    app.tcex.log.error(message)
                    if self.fail_msg:
                        app.exit_message = self.fail_msg  # for test cases
                        app.tcex.exit(1, self.fail_msg)
                    else:
                        app.exit_message = message
                        app.tcex.exit(1, message)
            # add results to kwargs
            kwargs[self.arg] = arg_data

            # Add logging for debug/troubleshooting
            arg_type = app.tcex.playbook.variable_type(getattr(app.args, self.arg))
            if arg_type not in ['Binary', 'BinaryArray'] and app.tcex.log.getEffectiveLevel() <= 10:
                # only log variable data to prevent logging keychain data
                if app.tcex.playbook.is_variable(arg):
                    log_string = str(arg_data)
                    if len(log_string) > 100:  # pragma: no cover
                        log_string = f'{log_string[:100]} ...'
                    app.tcex.log.debug(f'input value: {log_string}')

            return wrapped(*args, **kwargs)

        return read(instance, *args, **kwargs)
