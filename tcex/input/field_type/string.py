"""TcEx Framework Module"""

# standard library
import re
from collections.abc import Generator

# third-party
from pydantic.fields import ModelField  # TYPE-CHECKING

# first-party
from tcex.input.field_type.exception import (
    InvalidEmptyValue,
    InvalidLengthValue,
    InvalidPatternValue,
    InvalidType,
)


class String(str):
    """String Field Type"""

    allow_empty: bool = True
    max_length: int | None = None
    min_length: int | None = None
    regex: str | None = None
    strip: bool = False

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Run validators / modifiers on input."""
        yield cls.validate_type
        yield cls.validate_strip
        yield cls.validate_allow_empty
        yield cls.validate_max_length
        yield cls.validate_min_length
        yield cls.validate_regex

    @classmethod
    def validate_allow_empty(cls, value: str, field: ModelField) -> str:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False:
            if isinstance(value, str) and value == '':
                raise InvalidEmptyValue(field_name=field.name)

        return value

    @classmethod
    def validate_max_length(cls, value: str, field: ModelField) -> str:
        """Raise exception if value does not match pattern."""
        if cls.max_length is not None and len(value) > cls.max_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.max_length, operation='max'
            )
        return value

    @classmethod
    def validate_min_length(cls, value: str, field: ModelField) -> str:
        """Raise exception if value does not match pattern."""
        if cls.min_length is not None and len(value) < cls.min_length:
            raise InvalidLengthValue(
                field_name=field.name, constraint=cls.min_length, operation='min'
            )
        return value

    @classmethod
    def validate_regex(cls, value: str, field: ModelField) -> str:
        """Raise exception if value does not match pattern."""
        if isinstance(cls.regex, str):
            if not re.compile(cls.regex).match(value):
                raise InvalidPatternValue(field_name=field.name, pattern=cls.regex)
        return value

    @classmethod
    def validate_strip(cls, value: str) -> str:
        """Raise exception if value is not a Binary type."""
        if cls.strip is True:
            value = value.strip()
        return value

    @classmethod
    def validate_type(cls, value: str, field: ModelField) -> str:
        """Raise exception if value is not a String type."""
        if not isinstance(value, str):
            raise InvalidType(
                field_name=field.name, expected_types='(str)', provided_type=type(value)
            )
        return value


def string(
    allow_empty: bool = True,
    max_length: int | None = None,
    min_length: int | None = None,
    regex: str | None = None,
    strip: bool = False,
) -> type[String]:
    """Return configured instance of String."""
    namespace = {
        'allow_empty': allow_empty,
        'max_length': max_length,
        'min_length': min_length,
        'regex': regex,
        'strip': strip,
    }
    return type('ConstrainedString', (String,), namespace)
