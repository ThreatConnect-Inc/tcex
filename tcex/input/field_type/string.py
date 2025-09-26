"""TcEx Framework Module"""

import re
from typing import Any, ClassVar

from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema  # TYPE-CHECKING

from tcex.input.field_type.exception import InvalidEmptyValue, InvalidPatternValue, InvalidType


class String(str):
    """String Field Type"""

    allow_empty: ClassVar[bool] = True
    max_length: ClassVar[int | None] = None
    min_length: ClassVar[int | None] = None
    regex: ClassVar[str | None] = None
    strip: ClassVar[bool] = False

    @classmethod
    def _validate(cls, value: str, info: core_schema.ValidationInfo) -> str:
        """."""
        field_name = info.field_name or '--unknown--'
        value = cls.validate_type(value, field_name)
        value = cls.validate_regex(value, field_name)
        value = cls.validate_strip(value)
        value = cls.validate_allow_empty(value, field_name)
        return value  # noqa: RET504

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        """Run validators / modifiers on input."""
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(max_length=cls.max_length, min_length=cls.min_length),
            field_name=handler.field_name,
        )

    @classmethod
    def validate_allow_empty(cls, value: str, field_name: str) -> str:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False and value in (b'', ''):
            raise InvalidEmptyValue(field_name)
        return value

    @classmethod
    def validate_regex(cls, value: str, field_name: str) -> str:
        """Raise exception if value does not match pattern."""
        if isinstance(cls.regex, str) and not re.compile(cls.regex).match(value):
            raise InvalidPatternValue(field_name=field_name, pattern=cls.regex)
        return value

    @classmethod
    def validate_strip(cls, value: str) -> str:
        """Raise exception if value is not a Binary type."""
        if value is not None and cls.strip is True:
            value = value.strip()
        return value

    @classmethod
    def validate_type(cls, value: str, field_name: str) -> str:
        """Raise exception if value is not a Binary type."""
        if not isinstance(value, str):
            raise InvalidType(field_name, type(value))
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
