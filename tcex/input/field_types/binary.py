"""Binary Field Type"""
# standard library
from collections.abc import Generator

# third-party
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_types.exception import (
    InvalidEmptyValue,
    InvalidLengthValue,
    InvalidType,
    InvalidVariableType,
)
from tcex.utils.variables import BinaryVariable  # TYPE-CHECKING


class Binary(bytes):
    """Binary Field Type"""

    allow_empty: bool = True
    max_length: int = None
    min_length: int = None
    strip: bool = False

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Run validators / modifiers on input."""
        yield cls.validate_variable_type
        yield cls.validate_type
        yield cls.validate_strip
        yield cls.validate_allow_empty
        yield cls.validate_max_length
        yield cls.validate_min_length

    @classmethod
    def validate_allow_empty(cls, value: bytes | BinaryVariable, field: ModelField) -> 'bytes':
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False and value == b'':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    @classmethod
    def validate_max_length(cls, value: str | BinaryVariable, field: ModelField) -> str:
        """Raise exception if value does not match pattern."""
        if cls.max_length is not None and len(value) > cls.max_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.max_length, operation='max'
            )
        return value

    @classmethod
    def validate_min_length(cls, value: str | BinaryVariable, field: ModelField) -> str:
        """Raise exception if value does not match pattern."""
        if cls.min_length is not None and len(value) < cls.min_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.min_length, operation='min'
            )
        return value

    @classmethod
    def validate_strip(cls, value: bytes | BinaryVariable) -> bytes:
        """Raise exception if value is not a Binary type."""
        if value is not None and cls.strip is True:
            value = value.strip()
        return value

    @classmethod
    def validate_type(cls, value: bytes | BinaryVariable, field: ModelField) -> bytes:
        """Raise exception if value is not a Binary type."""
        if not isinstance(value, bytes):
            raise InvalidType(
                field_name=field.name, expected_types='(str)', provided_type=type(value)
            )
        return value

    @classmethod
    def validate_variable_type(cls, value: bytes | BinaryVariable, field: ModelField) -> bytes:
        """Raise exception if value is not a Binary type."""
        if hasattr(value, '_variable_type') and value._variable_type != 'Binary':
            raise InvalidVariableType(
                field_name=field.name, expected_type='Binary', provided_type=value._variable_type
            )
        return value


def binary(
    allow_empty: bool = True,
    min_length: int | None = None,
    max_length: int | None = None,
    strip: bool = False,
) -> type:
    """Return customized Binary type."""
    namespace = {
        'allow_empty': allow_empty,
        'max_length': max_length,
        'min_length': min_length,
        'strip': strip,
    }
    return type('CustomizedBinary', (Binary,), namespace)
