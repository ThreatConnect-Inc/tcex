"""TcEx Framework Module"""

import logging
from typing import Any, ClassVar, Self

from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic_core import core_schema

from tcex.input.field_type.exception import InvalidEmptyValue, InvalidType
from tcex.logger.sensitive_filter import SensitiveFilter
from tcex.logger.trace_logger import TraceLogger
from tcex.util.variable import BinaryVariable

# get tcex logger
filter_sensitive = SensitiveFilter(name='sensitive_filter')
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore
_logger.addFilter(filter_sensitive)


class Sensitive:
    """Sensitive Field Type"""

    allow_empty: ClassVar[bool] = True
    min_length: ClassVar[int | None] = None
    max_length: ClassVar[int | None] = None

    def __init__(self, value: bytes | str | Self):
        """Initialize the Sensitive object."""
        if isinstance(value, Sensitive):
            self._sensitive_value = value.value
        elif isinstance(value, bytes):
            self._sensitive_value = value.decode()
        else:
            self._sensitive_value = value
        filter_sensitive.add(self._sensitive_value)

    @classmethod
    def _validate(cls, value: bytes | str | Self, info: core_schema.ValidationInfo) -> Self:
        """Define one or more validators for Pydantic custom type."""
        field_name = info.field_name or '--unknown--'
        value = cls.validate_type(value, field_name)
        value = cls.validate_allow_empty(value, field_name)
        return cls.wrap_type(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.AfterValidatorFunctionSchema:
        """Run validators / modifiers on input."""
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(
                coerce_numbers_to_str=True,
                max_length=cls.max_length,
                min_length=cls.min_length,
                strict=False,
            ),
            field_name=handler.field_name,
        )

    def __len__(self) -> int:
        """Return the length of the sensitive value."""
        return len(self._sensitive_value)

    # @classmethod
    # def __modify_schema__(cls, field_schema: dict[str, Any]):
    #     """Modify the field schema."""

    #     def _update_not_none(mapping: dict[Any, Any], **update: Any):
    #         mapping.update({k: v for k, v in update.items() if v is not None})

    #     _update_not_none(
    #         field_schema,
    #         type='string',
    #         writeOnly=True,
    #         format='password',
    #         minLength=cls.min_length,
    #         maxLength=cls.max_length,
    #     )

    def __repr__(self) -> str:
        """."""
        return f'Sensitive("{self}")'

    def __str__(self) -> str:
        """Return the value masked.

        If App is running in > DEBUG logging level and the sensitive data is greater
        than X, then show the first and last character of the value. This is very
        helpful in debugging App where the incorrect credential could have been passed.
        """
        # DEBUG or TRACE
        trace_log_level = 10
        if (
            self._sensitive_value
            and _logger.getEffectiveLevel() <= trace_log_level
            and isinstance(self.value, str)
            and len(self.value) >= trace_log_level
        ):
            return f'{self.value[:1]}{"*" * 4}{self.value[-1:]}'
        return '**********'

    @classmethod
    def validate_allow_empty(cls, value: bytes | str | Self, field_name: str) -> bytes | str | Self:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False:
            if isinstance(value, str) and value.replace(' ', '') == '':
                raise InvalidEmptyValue(field_name=field_name)
            if isinstance(value, bytes) and value == b'':
                raise InvalidEmptyValue(field_name=field_name)
            if isinstance(value, Sensitive) and value.value.replace(' ', '') == '':
                raise InvalidEmptyValue(field_name=field_name)
        return value

    @classmethod
    def validate_type(cls, value: bytes | str | Self, field_name: str) -> bytes | str | Self:
        """Raise exception if value is not a String type."""
        if not isinstance(value, bytes | str | Sensitive):
            raise InvalidType(
                field_name=field_name, expected_types='(bytes, str)', provided_type=str(type(value))
            )
        return value

    @property
    def value(self) -> str:
        """Return the actual value."""
        if not isinstance(self._sensitive_value, BinaryVariable | bytes):
            # file variables can be used for client certs, json credential,
            # etc and the data is provided as a BinaryVariable object. This
            # is a special case where we need to return the value as a string.
            return str(self._sensitive_value)
        return self._sensitive_value

    @classmethod
    def wrap_type(cls, value: bytes | str | Self) -> Self:
        """Raise exception if value is not a String type."""
        return cls(value)


def sensitive(
    allow_empty: bool = True,
    max_length: int | None = None,
    min_length: int | None = None,
) -> type[Sensitive]:
    """Return configured instance of String."""
    namespace = {
        'allow_empty': allow_empty,
        'max_length': max_length,
        'min_length': min_length,
    }
    return type('ConstrainedSensitive', (Sensitive,), namespace)
