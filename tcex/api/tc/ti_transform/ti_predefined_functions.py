"""TcEx Framework Module"""

# standard library
import json
from functools import wraps
from inspect import signature
from typing import TypedDict

# first-party
from tcex.util import Util


class ParamDefinition(TypedDict):
    name: str
    label: str
    type: str
    help: str


class FunctionDefinition(TypedDict):
    name: str
    label: str
    params: list[ParamDefinition]


def return_none_for_empty(fn):
    """Decorator that before running the wrapped function, checks for an empty value."""

    EMPTY_VALUES = (None, '', [], {})

    @wraps(fn)
    def _wrapper(value, *args, **kwargs):
        if value in EMPTY_VALUES:
            return None
        return fn(value, *args, **kwargs)

    return _wrapper


def custom_function_definition(definition: FunctionDefinition):
    """Attach a custom function definition to the function."""

    def _decorator(fn):
        setattr(fn, '_tcex_function_definition', definition)
        return fn

    return _decorator


class ProcessingFunctions:
    """Predefined functions to use in transforms."""

    def __init__(self, tcex) -> None:
        """."""
        self.tcex = tcex

    @return_none_for_empty
    def static_map(self, value, mapping: dict):
        """Map values to static values.

        If there is no matching value in the mapping the original value will be returned.
        """
        return mapping.get(str(value), value)

    @return_none_for_empty
    def value_in(self, value, values: str, delimiter: str):
        """Return the value if it is in the list of values, else return None."""
        if not values.startswith('"'):
            values.replace('"', '\"')
            Values = f'"{values}"'

        if not delimiter:
            Delimiter = ','

        return value if value in [v.strip() for v in json.loads(Values).split(Delimiter)] else None

    @custom_function_definition(
        {
            'name': 'format_table',
            'label': 'Format Objects as Markdown Table',
            'params': [
                {
                    'name': 'column_order',
                    'label': 'Column Order',
                    'type': 'str',
                    'help': 'The order of the columns.',
                }
            ],
        }
    )
    @return_none_for_empty
    def format_table(self, value, column_order: str):
        """Format a markdown table.

        value should be a list of objects that all have the same attributes.  The table will contain
        one row for each object in the list, and one column for each attribute of the objects.

        Keyword Args:
            Column Order - The order of the columns.
        """
        if column_order:
            order = [c.strip() for c in column_order.split(',')]
        else:
            order = list(value[0].keys())

        table = ''
        table += f'|{"|".join(order) }|\n'
        table += f'|{"|".join(["-" for o in order]) }|\n'
        for row in value:
            table += f'|{"|".join([str(row.get(o, "")) for o in order]) }|\n'

        return table

    @return_none_for_empty
    def any_to_datetime(self, value):
        """Convert any value to a datetime object."""
        return self.tcex.util.any_to_datetime(value)

    @return_none_for_empty
    def append(self, value, suffix: str):
        """Append a value to the input value."""
        return f'{value}{suffix}'

    @return_none_for_empty
    def prepend(self, value, prefix: str):
        """Prepend a value to the input value."""
        return f'{prefix}{value}'

    @return_none_for_empty
    def replace(self, value, old_value: str, new_value: str):
        """Replace a value in the input value."""
        return value.replace(old_value, new_value)

    @return_none_for_empty
    def to_uppercase(self, value):
        """Convert value to uppercase."""
        return str.upper(value)

    @return_none_for_empty
    def to_lowercase(self, value):
        """Convert value to lowercase."""
        return str.lower(value)

    @return_none_for_empty
    def to_titlecase(self, value):
        """Convert value to titlecase."""
        return str.title(value)

    @return_none_for_empty
    def truncate(self, value, length: int, append_chars: str):
        """Truncate a string."""
        return self.tcex.util.truncate_string(value, length=length, append_chars=append_chars)

    @classmethod
    def get_function_definitions(cls) -> list[FunctionDefinition]:
        """Get function definitions in JSON format, suitable for the transform builder UI."""

        def _is_function(obj):
            return type(obj).__name__ == 'function'

        def _snake_to_tile_case(name):
            return name.replace('_', ' ').title()

        def _get_params_defs(fn) -> list[ParamDefinition]:
            """
            Get the arguments for a function.

            Args:
                fn (function): The function to get the arguments for.

            Returns:
                list: A list of dictionaries containing the argument name and type.
            """
            sig = signature(fn)
            params = [n for n in sig.parameters if n not in ('self', 'value')]
            return [
                {
                    'name': p,
                    'label': _snake_to_tile_case(p),
                    'type': (
                        sig.parameters[p].annotation.__name__
                        if sig.parameters[p].annotation
                        else 'str'
                    ),
                    'help': getattr(fn, '__doc__', ''),
                }
                for p in params
            ]

        fns = [
            fn
            for fn in (getattr(cls, n) for n in dir(cls) if not n.startswith('_'))
            if _is_function(fn)
        ]

        specs = [
            getattr(fn, '_tcex_function_definition', {})
            or {
                'name': fn.__name__,
                'label': _snake_to_tile_case(fn.__name__),
                'parmams': _get_params_defs(fn),
            }
            for fn in fns
        ]

        return specs  # type: ignore
