"""TcEx Framework Module"""

# standard library
from collections.abc import Generator

# third-party
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_type.exception import InvalidEmptyValue, InvalidLengthValue, InvalidType


class Binary(bytes):
    """Binary Field Type"""

    allow_empty: bool = True
    max_length: int | None = None
    min_length: int | None = None
    strip: bool = False

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Run validators / modifiers on input."""
        yield cls.validate_type
        yield cls.validate_strip
        yield cls.validate_allow_empty
        yield cls.validate_max_length
        yield cls.validate_min_length

    @classmethod
    def validate_allow_empty(cls, value: bytes, field: ModelField) -> bytes:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False and value == b'':
            raise InvalidEmptyValue(field_name=field.name)
        return value

    @classmethod
    def validate_max_length(cls, value: bytes, field: ModelField) -> bytes:
        """Raise exception if value does not match pattern."""
        if cls.max_length is not None and len(value) > cls.max_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.max_length, operation='max'
            )
        return value

    @classmethod
    def validate_min_length(cls, value: bytes, field: ModelField) -> bytes:
        """Raise exception if value does not match pattern."""
        if cls.min_length is not None and len(value) < cls.min_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.min_length, operation='min'
            )
        return value

    @classmethod
    def validate_strip(cls, value: bytes) -> bytes:
        """Raise exception if value is not a Binary type."""
        if value is not None and cls.strip is True:
            value = value.strip()
        return value

    @classmethod
    def validate_type(cls, value: bytes, field: ModelField) -> bytes:
        """Raise exception if value is not a Binary type."""
        if not isinstance(value, bytes):
            raise InvalidType(
                field_name=field.name, expected_types='(bytes)', provided_type=str(type(value))
            )
        return value


def binary(
    allow_empty: bool = True,
    min_length: int | None = None,
    max_length: int | None = None,
    strip: bool = False,
) -> Binary:
    """Return customized Binary type."""
    namespace = {
        'allow_empty': allow_empty,
        'max_length': max_length,
        'min_length': min_length,
        'strip': strip,
    }
    return type('CustomizedBinary', (Binary,), namespace)  # type: ignore
