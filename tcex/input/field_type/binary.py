"""TcEx Framework Module"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, ClassVar

from pydantic.annotated_handlers import GetCoreSchemaHandler  # noqa: TC002
from pydantic_core import core_schema  # TYPE-CHECKING

from tcex.input.field_type.exception import InvalidEmptyValue, InvalidType


@dataclass(frozen=True)
class Binary(bytes):
    """Binary Field Type"""

    allow_empty: ClassVar[bool] = True
    max_length: ClassVar[int | None] = None
    min_length: ClassVar[int | None] = None
    strip: ClassVar[bool] = False

    @classmethod
    def _validate(cls, value: bytes, info: core_schema.ValidationInfo) -> bytes:
        """."""
        field_name = info.field_name or '--unknown--'
        value = cls.validate_type(value, field_name)
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
            core_schema.bytes_schema(max_length=cls.max_length, min_length=cls.min_length),
            field_name=handler.field_name,
        )

    @classmethod
    def validate_allow_empty(cls, value: bytes, field_name: str) -> bytes:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False and value == b'':
            raise InvalidEmptyValue(field_name)
        return value

    @classmethod
    def validate_strip(cls, value: bytes) -> bytes:
        """Raise exception if value is not a Binary type."""
        if value is not None and cls.strip is True:
            value = value.strip()
        return value

    @classmethod
    def validate_type(cls, value: bytes, field_name: str) -> bytes:
        """Raise exception if value is not a Binary type."""
        if not isinstance(value, bytes):
            raise InvalidType(field_name, type(value))
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
