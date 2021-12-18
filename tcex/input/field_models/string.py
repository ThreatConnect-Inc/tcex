"""String Playbook Type"""
# standard library
import re
from typing import TYPE_CHECKING, Callable, Optional, Union

if TYPE_CHECKING:
    # first-party
    from tcex.input.input import StringVariable


class String(str):
    """Ensure an array is always returned for the input."""

    allow_empty: bool = True
    # conditional_required: Optional[Dict[str, str]] = None
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    regex: Optional[str] = None

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Run validators / modifiers on input."""
        yield cls.validate_variable_type
        yield cls.validate_type
        yield cls.validate_allow_empty
        # yield cls.validate_conditional_required
        yield cls.validate_max_length
        yield cls.validate_min_length
        yield cls.validate_regex

    @classmethod
    def validate_allow_empty(cls, value: Union[str, 'StringVariable']) -> str:
        """Raise exception if value is empty and allow_empty is False."""
        if cls.allow_empty is False:
            if (
                isinstance(value, str) and value.replace(' ', '') == ''
            ):  # None value are automatically covered
                raise ValueError('Empty value is not allowed.')

            if value == '':  # None value are automatically covered
                raise ValueError('Empty value is not allowed.')
        return value

    # @classmethod
    # def validate_conditional_required(
    #     cls, value: Union[str, 'StringVariable'], values: Dict[str, Any]
    # ) -> str:
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
    def validate_max_length(cls, value: Union[str, 'StringVariable']) -> str:
        """Raise exception if value does not match pattern."""
        if cls.max_length is not None and len(value) > cls.max_length:
            raise ValueError(f'Value length is above set max length of {cls.min_length}.')
        return value

    @classmethod
    def validate_min_length(cls, value: Union[str, 'StringVariable']) -> str:
        """Raise exception if value does not match pattern."""
        if cls.min_length is not None and len(value) < cls.min_length:
            raise ValueError(f'Value length is below set min length of {cls.min_length}.')
        return value

    @classmethod
    def validate_regex(cls, value: Union[str, 'StringVariable']) -> str:
        """Raise exception if value does not match pattern."""
        if isinstance(cls.regex, str):
            if not re.compile(cls.regex).match(value):
                raise ValueError(f'Value did not match pattern {cls.regex}.')
        return value

    @classmethod
    def validate_type(cls, value: Union[str, 'StringVariable']) -> str:
        """Raise exception if value is not a String type."""
        if not isinstance(value, str):
            raise ValueError(f'{value} is not a String type.')
        return value

    @classmethod
    def validate_variable_type(cls, value: Union[str, 'StringVariable']) -> str:
        """Raise exception if value is not a String type."""
        if hasattr(value, '_variable_type') and value._variable_type != 'String':
            raise ValueError(f'{value} is not a String type.')
        return value


def string(
    allow_empty: bool = True,
    # conditional_required: Optional[Dict[str, str]] = None,
    max_length: Optional[int] = None,
    min_length: Optional[int] = None,
    regex: Optional[str] = None,
) -> type:
    """Return configured instance of String."""
    namespace = dict(
        allow_empty=allow_empty,
        # conditional_required=conditional_required,
        max_length=max_length,
        min_length=min_length,
        regex=regex,
    )
    return type('ConstrainedString', (String,), namespace)
