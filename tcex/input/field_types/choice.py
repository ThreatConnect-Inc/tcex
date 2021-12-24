"""Choice Field Type"""
# standard library
import logging
from typing import TYPE_CHECKING, Any, Callable

# first-party
from tcex.input.field_types.exception import InvalidEmptyValue, InvalidType

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField


# get tcex logger
logger = logging.getLogger('tcex')


class Choice:
    """Choice Field Type"""

    def __init__(self, value):
        """Initialize choice type"""
        if isinstance(value, Choice):
            self._value = value.value
        else:
            self._value = value

    @property
    def value(self) -> str:
        """Return the selection. Return None if selection is '-- Select --'"""
        return None if self._value == '-- Select --' else self._value

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    @classmethod
    def _validate(cls, value: Any, field: 'ModelField') -> 'Choice':
        """Pydantic validate method."""
        if isinstance(value, cls):
            return value

        if not isinstance(value, (int, str)):
            raise InvalidType(
                field_name=field.name, expected_types='(int, str)', provided_type=type(value)
            )

        if isinstance(value, str) and value.replace(' ', '') == '':
            raise InvalidEmptyValue(field_name=field.name)

        return cls(value)
