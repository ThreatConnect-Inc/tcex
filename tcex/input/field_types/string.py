"""String Field Type"""
# standard library
import re
from typing import TYPE_CHECKING, Callable, Optional, Union

# first-party
from tcex.input.field_types.exception import (
    InvalidEmptyValue,
    InvalidLengthValue,
    InvalidPatternValue,
    InvalidType,
    InvalidVariableType,
)

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField

    # first-party
    from tcex.utils.variables import StringVariable


class String(str):
    """String Field Type"""

    allow_empty: bool = True
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    regex: Optional[str] = None
    strip: bool = False

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Run validators / modifiers on input."""
        yield cls.validate_variable_type
        yield cls.validate_type
        yield cls.validate_strip
        yield cls.validate_allow_empty
        yield cls.validate_max_length
        yield cls.validate_min_length
        yield cls.validate_regex

    @classmethod
    def validate_allow_empty(cls, value: Union[str, 'StringVariable'], field: 'ModelField') -> str:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False:
            if isinstance(value, str) and value == '':
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
    def validate_regex(cls, value: Union[str, 'StringVariable'], field: 'ModelField') -> str:
        """Raise exception if value does not match pattern."""
        if isinstance(cls.regex, str):
            if not re.compile(cls.regex).match(value):
                raise InvalidPatternValue(field_name=field.name, pattern=cls.regex)
        return value

    @classmethod
    def validate_strip(cls, value: Union[bytes, 'StringVariable']) -> bytes:
        """Raise exception if value is not a Binary type."""
        if cls.strip is True:
            value = value.strip()
        return value

    @classmethod
    def validate_type(cls, value: Union[str, 'StringVariable'], field: 'ModelField') -> str:
        """Raise exception if value is not a String type."""
        if not isinstance(value, str):
            raise InvalidType(
                field_name=field.name, expected_types='(str)', provided_type=type(value)
            )
        return value

    @classmethod
    def validate_variable_type(
        cls, value: Union[str, 'StringVariable'], field: 'ModelField'
    ) -> str:
        """Raise exception if value is not a String type."""
        if hasattr(value, '_variable_type') and value._variable_type != 'String':
            raise InvalidVariableType(
                field_name=field.name, expected_type='String', provided_type=value._variable_type
            )
        return value


def string(
    allow_empty: bool = True,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    regex: Optional[str] = None,
    strip: bool = False,
) -> type:
    """Return configured instance of String."""
    namespace = dict(
        allow_empty=allow_empty,
        max_length=max_length,
        min_length=min_length,
        regex=regex,
        strip=strip,
    )
    return type('ConstrainedString', (String,), namespace)
