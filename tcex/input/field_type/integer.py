"""TcEx Framework Module"""

# standard library
from collections.abc import Generator
from typing import Any

# third-party
from pydantic.fields import ModelField  # TYPE-CHECKING
from pydantic.types import OptionalInt

# first-party
from tcex.input.field_type.exception import InvalidIntegerValue, InvalidType


class Integer(int):
    """Integer Field Type"""

    ge: OptionalInt = None
    gt: OptionalInt = None
    le: OptionalInt = None
    lt: OptionalInt = None

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]):
        """Modify the field schema."""

        def update_not_none(mapping: dict[Any, Any], **update: Any):
            mapping.update({k: v for k, v in update.items() if v is not None})

        update_not_none(
            field_schema,
            exclusiveMinimum=cls.gt,
            exclusiveMaximum=cls.lt,
            minimum=cls.ge,
            maximum=cls.le,
        )

    @classmethod
    def __get_validators__(cls) -> Generator:
        """Run validators / modifiers on input."""
        yield cls.validate_type
        yield cls.validate_value

    @classmethod
    def validate_type(cls, value: int | str, field: ModelField) -> int | str:
        """Raise exception if value is not a String type."""
        if not isinstance(value, int | str):
            raise InvalidType(
                field_name=field.name, expected_types='(int, str)', provided_type=type(value)
            )
        return value

    @classmethod
    def validate_value(cls, value: int | str, field: ModelField) -> int:
        """Raise exception if value does not meet criteria."""
        if isinstance(value, str):
            value = int(value)

        if cls.ge is not None and not value >= cls.ge:
            raise InvalidIntegerValue(
                field_name=field.name, operation='greater than or equal to', constraint=cls.ge
            )
        if cls.gt is not None and not value > cls.gt:
            raise InvalidIntegerValue(
                field_name=field.name, operation='greater than', constraint=cls.gt
            )

        if cls.le is not None and not value <= cls.le:
            raise InvalidIntegerValue(
                field_name=field.name, operation='less than or equal to', constraint=cls.le
            )
        if cls.lt is not None and not value < cls.lt:
            raise InvalidIntegerValue(
                field_name=field.name, operation='less than', constraint=cls.lt
            )
        return value


def integer(
    gt: OptionalInt = None,
    ge: OptionalInt = None,
    lt: OptionalInt = None,
    le: OptionalInt = None,
) -> type[Integer]:
    """Return configured instance of String."""
    namespace = {
        'gt': gt,
        'ge': ge,
        'lt': lt,
        'le': le,
    }
    return type('ConstrainedInteger', (Integer,), namespace)
