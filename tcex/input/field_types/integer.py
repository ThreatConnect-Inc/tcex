"""Integer Field Type"""
# standard library
from typing import TYPE_CHECKING, Any, Callable, Dict, Union

# third-party
from pydantic.types import OptionalInt

# first-party
from tcex.input.field_types.exception import InvalidIntegerValue, InvalidType, InvalidVariableType

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from pydantic.fields import ModelField

    # first-party
    from tcex.utils.variables import StringVariable


class Integer(int):
    """Integer Field Type"""

    ge: OptionalInt = None
    gt: OptionalInt = None
    le: OptionalInt = None
    lt: OptionalInt = None

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]):
        """Modify the field schema."""

        def update_not_none(mapping: Dict[Any, Any], **update: Any):
            mapping.update({k: v for k, v in update.items() if v is not None})

        update_not_none(
            field_schema,
            exclusiveMinimum=cls.gt,
            exclusiveMaximum=cls.lt,
            minimum=cls.ge,
            maximum=cls.le,
        )

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Run validators / modifiers on input."""
        yield cls.validate_variable_type
        yield cls.validate_type
        yield cls.validate_value

    @classmethod
    def validate_type(cls, value: Union[int, str, 'StringVariable'], field: 'ModelField') -> int:
        """Raise exception if value is not a String type."""
        if not isinstance(value, (int, str)):
            raise InvalidType(
                field_name=field.name, expected_types='(int, str)', provided_type=type(value)
            )
        return value

    @classmethod
    def validate_value(cls, value: Union[int, str, 'StringVariable'], field: 'ModelField') -> int:
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

    @classmethod
    def validate_variable_type(
        cls, value: Union[int, str, 'StringVariable'], field: 'ModelField'
    ) -> int:
        """Raise exception if value is not a String type."""
        if hasattr(value, '_variable_type') and value._variable_type != 'String':
            raise InvalidVariableType(
                field_name=field.name, expected_type='String', provided_type=value._variable_type
            )
        return value


def integer(
    gt: OptionalInt = None,
    ge: OptionalInt = None,
    lt: OptionalInt = None,
    le: OptionalInt = None,
) -> type:
    """Return configured instance of String."""
    namespace = dict(
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
    )
    return type('ConstrainedInteger', (Integer,), namespace)
