"""String Playbook Type"""
# standard library
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Union

# third-party
from pydantic.types import OptionalInt

if TYPE_CHECKING:
    # first-party
    from tcex.input.input import StringVariable


class Integer(int):
    """Ensure an array is always returned for the input."""

    ge: OptionalInt = None
    gt: OptionalInt = None
    le: OptionalInt = None
    lt: OptionalInt = None
    return_array: bool = False

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        """Modify the field schema."""

        def update_not_none(mapping: Dict[Any, Any], **update: Any) -> None:
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
        yield cls.validate_return_array

    @classmethod
    def validate_return_array(cls, value: Union[int, str, 'StringVariable']) -> List[int]:
        """Return an array if return_array is True."""
        if cls.return_array is True and not isinstance(value, list):
            return [value]
        return value

    @classmethod
    def validate_type(cls, value: Union[int, str, 'StringVariable']) -> int:
        """Raise exception if value is not a String type."""
        if not isinstance(
            value,
            (
                int,
                str,
            ),
        ):
            raise ValueError(f'{value} is not the correct type.')
        return value

    @classmethod
    def validate_value(cls, value: Union[int, str, 'StringVariable']) -> int:
        """Raise exception if value does not meet criteria."""
        print('value', value)
        value = int(value)
        if cls.gt is not None and not value > cls.gt:
            raise ValueError(f'Value must be greater than {cls.gt}.')
        if cls.ge is not None and not value >= cls.ge:
            raise ValueError(f'Value must be greater than or equal to {cls.ge}.')

        if cls.lt is not None and not value < cls.lt:
            raise ValueError(f'Value must be less than {cls.lt}.')
        if cls.le is not None and not value <= cls.le:
            raise ValueError(f'Value must be less than or equal to {cls.le}.')
        return value

    @classmethod
    def validate_variable_type(cls, value: Union[int, str, 'StringVariable']) -> int:
        """Raise exception if value is not a String type."""
        if hasattr(value, '_variable_type') and value._variable_type != 'String':
            raise ValueError(f'{value} is not a String type.')
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
