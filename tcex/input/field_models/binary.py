"""Binary Playbook Type"""
# standard library
from typing import TYPE_CHECKING, Callable, Union

if TYPE_CHECKING:
    # first-party
    from tcex.input.input import BinaryVariable


class Binary(bytes):
    """Ensure an array is always returned for the input."""

    allow_empty: bool = True
    # conditional_required: Optional[Dict[str, str]] = None
    max_length: int = None
    min_length: int = None

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Run validators / modifiers on input."""
        yield cls.validate_variable_type
        yield cls.validate_type
        yield cls.validate_allow_empty
        # yield cls.validate_conditional_required
        yield cls.validate_max_length
        yield cls.validate_min_length

    @classmethod
    def validate_allow_empty(cls, value: Union[bytes, 'BinaryVariable']) -> 'bytes':
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False and value == b'':
            raise ValueError('Empty binary values are not allowed.')
        return value

    # @classmethod
    # def validate_conditional_required(
    #     cls, value: Union[bytes, 'BinaryVariable'], values: Dict[str, Any]
    # ) -> bytes:
    #     """Raise exception the value is conditionally required.

    #     The conditional value must be present in the values dict before the
    #     dependent value.
    #     """
    #     # you could have more than 1 conditions
    #     if cls.conditional_required is not None:
    #         for k, v in cls.conditional_required.items():
    #             if values.get(k) == v and not value:
    #                 raise ValueError(f'Value is required when "{k}" equals "{v}".')
    #     return value

    @classmethod
    def validate_max_length(cls, value: Union[str, 'BinaryVariable']) -> str:
        """Raise exception if value does not match pattern."""
        if cls.max_length is not None and len(value) > cls.max_length:
            raise ValueError(f'Value length is above set max length of {cls.min_length}.')
        return value

    @classmethod
    def validate_min_length(cls, value: Union[str, 'BinaryVariable']) -> str:
        """Raise exception if value does not match pattern."""
        if cls.min_length is not None and len(value) < cls.min_length:
            raise ValueError(f'Value length is below set min length of {cls.min_length}.')
        return value

    @classmethod
    def validate_type(cls, value: Union[bytes, 'BinaryVariable']) -> bytes:
        """Raise exception if value is not a Binary type."""
        if not isinstance(value, bytes):
            raise ValueError(f'{value} is not a Binary type.')
        return value

    @classmethod
    def validate_variable_type(cls, value: Union[bytes, 'BinaryVariable']) -> bytes:
        """Raise exception if value is not a Binary type."""
        if hasattr(value, '_variable_type') and value._variable_type != 'Binary':
            raise ValueError(f'{value} is not a Binary type.')
        return value


def binary(
    allow_empty: bool = True,
    # conditional_required: Optional[Dict[str, bytes]] = None,
    min_length: int = None,
    max_length: int = None,
) -> type:
    """Return configured instance of Binary."""
    namespace = dict(
        allow_empty=allow_empty,
        # conditional_required=conditional_required,
        max_length=max_length,
        min_length=min_length,
    )
    return type('ConstrainedBinary', (Binary,), namespace)
