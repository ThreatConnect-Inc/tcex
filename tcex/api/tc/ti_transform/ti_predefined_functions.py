"""TcEx Framework Module"""

# standard library
import hashlib
import json
import uuid
from collections.abc import Iterable
from inspect import _empty, signature
from typing import TypedDict

# first-party
# first-part
from tcex.api.tc.ti_transform.model.transform_model import (
    GroupTransformModel,
    IndicatorTransformModel,
)


class TransformBuilderExport(TypedDict):
    """Basic definition of a transform exported from Transform Builder."""

    type: str
    transform: dict


def transform_builder_to_model(
    transform: TransformBuilderExport,
    processing_functions: 'ProcessingFunctions',
) -> IndicatorTransformModel | GroupTransformModel:
    """Convert a transform from Transform Builder to one of the tcex transform models."""

    def find_entries(data, key, context='') -> Iterable[tuple[str, dict]]:
        """Find entries in a dict with a given name, regardless of depth."""
        if isinstance(data, dict):
            for k, v in data.items():
                if k == key:
                    yield (context, v)
                elif isinstance(v, (dict, list)):
                    yield from find_entries(v, key, context=f'{context}.{k}' if context else k)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                yield from find_entries(item, key, context=f'{context}[{i}]')

    for context, processing in find_entries(transform['transform'], 'transform'):
        if not isinstance(processing, list):
            processing = [processing]

        for step in processing:
            fn_name = step.get('for_each') or step.get('method')
            step.update(
                processing_functions.translate_def_to_fn(
                    step,
                    f'{context}, Processing Function: '
                    f'{processing_functions._snake_to_titlecase(fn_name)}',
                )
            )

    match transform['type'].lower():
        case 'indicator':
            return IndicatorTransformModel(**transform['transform'])
        case 'group':
            return GroupTransformModel(**transform['transform'])
        case _:
            raise TypeError(f'Unknown transform type: {transform["type"]}')


class ParamDefinition(TypedDict):
    """Parameter definition for use in the transform builder UI."""

    default: str | None
    help: str
    label: str
    name: str
    required: bool
    type: str


class FunctionDefinition(TypedDict):
    """Function definition for use in the transform builder UI."""

    name: str
    label: str
    help: str
    params: list[ParamDefinition]


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
        self.custom_fns = {}

    @custom_function_definition(
        {
            'name': 'custom',
            'label': 'Custom',
            'help': 'Describe a custom processing function.',
            'params': [
                {
                    'default': None,
                    'name': 'name',
                    'label': 'Name',
                    'type': 'str',
                    'help': 'A unique name for this custom processing function.',
                    'required': True,
                },
                {
                    'default': None,
                    'name': 'description',
                    'label': 'Description',
                    'type': 'str',
                    'help': 'Describe the custom processing function.',
                    'required': True,
                },
            ],
        }
    )
    def custom(self, value, name: str, description: str, ti_dict, transform, **kwargs):
        """Allow for custom processing to be described."""
        fn = self.custom_fns.get(name.lower())
        if not fn:
            raise NotImplementedError(f'Custom function not implemented: {description}')
        return fn(value, ti_dict=ti_dict, transform=transform, **kwargs)

    def static_map(self, value, mapping: dict):
        """Map values to static values.

        If there is no matching value in the mapping the original value will be returned.
        """
        if not isinstance(mapping, dict):
            mapping = json.loads(mapping)
        return mapping.get(str(value), value)

    def value_in(self, value, values: str, delimiter: str = ','):
        """Return the value if it is in the list of values, else return None."""
        if not values.startswith('"'):
            values.replace('"', '\"')
            values = f'"{values}"'

        return value if value in [v.strip() for v in json.loads(values).split(delimiter)] else None

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

    def any_to_datetime(self, value):
        """Convert any value to a datetime object."""
        return self.tcex.util.any_to_datetime(value).isoformat()

    def append(self, value, suffix: str):
        """Append a value to the input value."""
        return f'{value}{suffix}'

    def prepend(self, value, prefix: str):
        """Prepend a value to the input value."""
        return f'{prefix}{value}'

    def replace(self, value, old_value: str, new_value: str = ''):
        """Replace a value in the input value."""
        return value.replace(old_value, new_value)

    def to_uppercase(self, value):
        """Convert value to uppercase."""
        return str.upper(value)

    def to_lowercase(self, value):
        """Convert value to lowercase."""
        return str.lower(value)

    def to_titlecase(self, value):
        """Convert value to titlecase."""
        return str.title(value)

    def truncate(self, value, length: int, append_chars: str = '...'):
        """Truncate a string."""
        return self.tcex.util.truncate_string(value, length=length, append_chars=append_chars)

    def hash(self, value) -> str:
        """Hash the given value."""
        return hashlib.sha256(str(value).encode('utf-8')).hexdigest()

    def split(self, value, delimiter: str = ','):
        """Split a string into a list."""
        return [v.strip() for v in value.split(delimiter)]

    def remove_surrounding_whitespace(self, value):
        """Strip leading and trailing whitespace from a string."""
        return value.strip()

    @custom_function_definition({'name': 'uuid5', 'label': 'To UUID5', 'help': '', 'params': []})
    def uuid5(self, value, namespace=None) -> str:
        """Generate a UUID5."""
        return str(uuid.uuid5(namespace or uuid.NAMESPACE_DNS, value))

    def convert_to_MITRE_tag(self, value) -> str | None:
        """Transform MITRE tags to TC format."""
        return self.tcex.api.tc.v3.mitre_tags.get_by_id_regex(value, value)

    def translate_def_to_fn(self, api_def: dict, context: str):
        """Translate a function definition in transform builder/API format to an actual function."""
        additional_context = ''
        try:
            translated = api_def.copy()

            type_ = 'method' if 'method' in api_def else 'for_each'

            if not type_:
                raise ValueError('No method or for_each key found in definition.')

            fn_name = api_def[type_]

            if callable(fn_name):
                return api_def

            fn = getattr(self, fn_name)

            if not fn:
                raise ValueError(f'Unknown function: {fn_name}')

            translated[type_] = fn

            if 'kwargs' in api_def:
                sig = signature(fn)

                for kwarg in api_def['kwargs']:
                    if kwarg not in sig.parameters:
                        raise ValueError(f'Unknown argument {kwarg} for function {fn_name}')

                    annotation = sig.parameters[kwarg].annotation
                    additional_context = f', Argument: {kwarg}'
                    match annotation():
                        case dict():
                            translated['kwargs'][kwarg] = json.loads(api_def['kwargs'][kwarg])
                        case _:
                            translated['kwargs'][kwarg] = sig.parameters[kwarg].annotation(
                                api_def['kwargs'][kwarg]
                            )

            return translated
        except Exception as e:
            # first-party
            from tcex.api.tc.ti_transform import TransformException

            raise TransformException(f'{context}{additional_context}', e, context=api_def)

    def get_function_definitions(self) -> list[FunctionDefinition]:
        """Get function definitions in JSON format, suitable for the transform builder UI."""

        def _is_function(obj):
            return type(obj).__name__ == 'method'

        fns = [
            fn
            for fn in (
                getattr(self, n)
                for n in dir(self)
                if not n.startswith('_')
                and n not in ('get_function_definitions', 'translate_def_to_fn')
            )
            if _is_function(fn)
        ]

        specs = [
            getattr(fn, '_tcex_function_definition', {})
            or {
                'name': fn.__name__,
                'label': self._snake_to_titlecase(fn.__name__),
                'params': self._get_params_defs(fn),
                'help': getattr(fn, '__doc__', ''),
            }
            for fn in fns
        ]

        return specs  # type: ignore

    @staticmethod
    def _snake_to_titlecase(name):
        return name.replace('_', ' ').title()

    @staticmethod
    def _get_params_defs(fn) -> list[ParamDefinition]:
        """Get the arguments for a function.

        Args:
            fn (function): The function to get the arguments for.

        Returns:
            list: A list of dictionaries containing the argument name and type.
        """
        sig = signature(fn)
        params = [n for n in sig.parameters if n not in ('self', 'value')]
        return [
            {
                'default': (
                    sig.parameters[p].default if sig.parameters[p].default != _empty else None
                ),
                'name': p,
                'label': ProcessingFunctions._snake_to_titlecase(p),
                'type': (
                    sig.parameters[p].annotation.__name__ if sig.parameters[p].annotation else 'str'
                ),
                'help': '',
                'required': True,
            }
            for p in params
        ]
