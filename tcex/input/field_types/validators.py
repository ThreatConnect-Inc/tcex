"""Model Validator/Modifier"""
# standard library
import operator
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

# third-party
from pydantic import BaseModel, validator

# first-party
from tcex.input.field_types.exception import InvalidEmptyValue, InvalidInput

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


def always_array(
    allow_empty: Optional[bool] = True,
    include_empty: Optional[bool] = False,
    include_null: Optional[bool] = False,
) -> List[Any]:
    """Return customized validator that always returns a list.

    Args:
        allow_empty: If True, return empty list if input is empty.
        include_empty: If True, will wrap empty string in list. This does not
            affect list with existing empty strings.
        include_null: If True, will wrap null value in list. This does not
            affect list with existing null values.
    """

    def _always_array(value: Any, field: 'ModelField') -> List[Any]:
        """Return validator."""
        if include_empty is True and value == '':
            value = [value]

        if include_null is True and value is None:
            value = [value]

        if value in (None, ''):
            value = []
        elif not isinstance(value, list):
            value = [value]

        if allow_empty is False and value == []:
            raise InvalidEmptyValue(field_name=field.name)

        return value

    return _always_array


def conditional_required(rules: List[Dict[str, str]] = True) -> Any:
    """Return customized validator that validates conditional required fields.

    Example Usage:

    If the severity field is set to 'High' the action field is required.

    MyModel(BaseModel):
        severity: str  # Low, Medium, High
        action: Optional[str]

        _conditional_required = validator('action', allow_reuse=True, always=True, pre=True)(
            conditional_required(
                rules=[{'field': 'severity', 'operation': 'eq', 'value': 'High'}]
            )
        )
    """

    def is_in(input_: str, value: List) -> bool:
        """Return True if input is in value list."""
        return input_ in value

    def not_in(input_: str, value: List) -> bool:
        """Return True if input is NOT in value list."""
        return input_ not in value

    def get_operator(op):
        """Get the corresponding operator"""

        operators = {
            'eq': operator.eq,
            'in': is_in,
            'ne': operator.ne,
            'ni': not_in,
        }
        return operators.get(op, operator.eq)

    def _conditional_required(value: str, field: 'ModelField', values: Dict[str, Any]):
        """Return validator."""
        for rule in rules or []:
            # the conditional field must be set above the conditionally required field
            conditional_field = values.get(rule.get('field'))
            conditional_operator = get_operator(rule.get('op', 'eq'))
            conditional_value = rule.get('value')

            if conditional_operator(conditional_field, conditional_value) is True and not value:
                raise InvalidInput(field_name=field.name, error='input is conditionally required.')

        return value

    return _conditional_required


def entity_input(
    only_value: Optional[bool] = False, type_filter: Optional[List[str]] = None
) -> Union[str, List[Any]]:
    """Return customized validator.

    only_value:

    When accepting String and TCEntity as PB data types, it is often easier to always work with
    the value. This validator will ensure that only the value is returned.

    type_filter:

    When accepting a TCEntity/TCEntityArray as input, it is sometimes preferred not to fail
    when the wrong type is found, but to instead filter out the entities with the wrong types.

    Example Usage:

    MyModel(BaseModel):
        ip_address: Union[
            AddressEntity,
            ip_address(strip_port=True)
        ]

        _entity_field = validator('ip_address', allow_reuse=True)(entity_field(only_value=True))

    If input takes String, StringArray, TCEntity, and TCEntityArray it may be helpful to always
    return an array.
    """

    def _entity_input(
        value: Union['BaseModel', List['BaseModel'], str, List[str]], field: 'ModelField'
    ) -> Union[List[str], str]:
        """Return value from String or TCEntity."""

        def _get_value(value: Union[str, 'BaseModel']) -> Union['BaseModel', str]:
            """Return value"""
            if isinstance(value, BaseModel):
                if isinstance(type_filter, list) and value.type not in type_filter:
                    return None

                if only_value is True:
                    return value.value
            return value

        if isinstance(value, list):
            _values = []
            for v in value:
                _value = _get_value(v)
                if _value is not None:
                    _values.append(_value)
            value = _values
        else:
            value = _get_value(value)

        if field.allow_none is True and value in [[], None]:
            raise ValueError()

        return value

    return _entity_input


def modify_advanced_settings(input_name) -> Callable:
    """Return validator that parses an advanced settings string and returns a dictionary

    :param input_name: the name of the input (within the app model) that will receive the
    pipe-delimited advanced settings string. In other words, the name of the input field
    that this validator should act on to parse the pipe-delimited string into a dictionary
    """

    def _modify_advanced_settings(value: Any, field: 'ModelField') -> Dict[str, str]:
        """Return validator."""
        settings = {}

        if value is None:
            if field.allow_none:
                return value
            raise InvalidInput(
                field_name=field.name,
                error='Value for field is None (null) and field is not Optional',
            )

        # should never be anything other than string, but may be worth adding a check
        # in case advanced settings for playbooks/services are ever a thing
        if isinstance(value, str):
            entries = value.split('|')

            for entry in entries:
                key_value = entry.split('=', maxsplit=1)

                if len(key_value) == 1:
                    continue

                key, value = key_value
                key = key.strip()
                if not key:
                    continue

                if key in settings:
                    raise InvalidInput(
                        field_name=field.name,
                        error=f'Duplicate key "{key}" defined in Advanced Settings input.',
                    )

                settings[key] = value

        return settings

    return validator(input_name, pre=True, allow_reuse=True)(_modify_advanced_settings)
