"""Sensitive Field Type"""
# standard library
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Union

# first-party
from tcex.input.field_types.exception import InvalidEmptyValue, InvalidLengthValue, InvalidType
from tcex.logger.sensitive_filter import SensitiveFilter  # pylint: disable=no-name-in-module

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField

    # first-party
    from tcex.utils.variables import StringVariable


# get tcex logger
filter_sensitive = SensitiveFilter(name='sensitive_filter')
logger = logging.getLogger('tcex')
logger.addFilter(filter_sensitive)


class Sensitive:
    """Sensitive Field Type"""

    allow_empty: bool = True
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    def __init__(self, value: Union[str, 'Sensitive']):
        """Initialize the Sensitive object."""
        if isinstance(value, Sensitive):
            self._sensitive_value = value.value
        else:
            self._sensitive_value = value
        filter_sensitive.add(self._sensitive_value)

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls.validate_type
        yield cls.validate_allow_empty
        yield cls.validate_max_length
        yield cls.validate_min_length
        yield cls.wrap_type

    def __len__(self) -> int:
        """Return the length of the sensitive value."""
        return len(self._sensitive_value)

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]):
        """Modify the field schema."""

        def _update_not_none(mapping: Dict[Any, Any], **update: Any):
            mapping.update({k: v for k, v in update.items() if v is not None})

        _update_not_none(
            field_schema,
            type='string',
            writeOnly=True,
            format='password',
            minLength=cls.min_length,
            maxLength=cls.max_length,
        )

    def __repr__(self) -> str:
        """."""
        return f'''Sensitive('{self}')'''

    def __str__(self) -> str:
        """Return the value masked.

        If App is running in > DEBUG logging level and the sensitive data is greater
        than X, then show the first and last character of the value. This is very
        helpful in debugging App where the incorrect credential could have been passed.
        """
        if self._sensitive_value and logger.getEffectiveLevel() <= 10:  # DEBUG or TRACE
            if isinstance(self.value, str) and len(self.value) >= 10:
                return f'''{self.value[:1]}{'*' * 4}{self.value[-1:]}'''
        return '**********'

    @classmethod
    def validate_allow_empty(cls, value: Union[str, 'StringVariable'], field: 'ModelField') -> str:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False:
            if isinstance(value, str) and value.replace(' ', '') == '':
                raise InvalidEmptyValue(field_name=field.name)

        return value

    @classmethod
    def validate_max_length(cls, value: Union[str, 'StringVariable'], field: 'ModelField') -> str:
        """Raise exception if value does not match pattern."""
        if cls.max_length is not None and len(value) > cls.max_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.max_length, operation='max'
            )
        return value

    @classmethod
    def validate_min_length(cls, value: Union[str, 'StringVariable'], field: 'ModelField') -> str:
        """Raise exception if value does not match pattern."""
        if cls.min_length is not None and len(value) < cls.min_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.min_length, operation='min'
            )
        return value

    @classmethod
    def validate_type(cls, value: Union[str, 'StringVariable'], field: 'ModelField') -> str:
        """Raise exception if value is not a String type."""
        if not isinstance(value, (bytes, str, Sensitive)):
            raise InvalidType(
                field_name=field.name, expected_types='(bytes, str)', provided_type=type(value)
            )
        return value

    @property
    def value(self) -> str:
        """Return the actual value."""
        return self._sensitive_value

    @classmethod
    def wrap_type(cls, value: Union[str, 'StringVariable']) -> str:
        """Raise exception if value is not a String type."""
        return cls(value)


def sensitive(
    allow_empty: bool = True,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
) -> type:
    """Return configured instance of String."""
    namespace = dict(
        allow_empty=allow_empty,
        max_length=max_length,
        min_length=min_length,
    )
    return type('ConstrainedSensitive', (Sensitive,), namespace)
