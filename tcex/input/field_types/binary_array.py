"""Always Array Validator"""
# standard library
from typing import Callable, Union

# first-party
from tcex.input.field_types.utils import array_validator


class BinaryArray(list):
    """BinaryArray Field Types"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['Binary', 'BinaryArray']
    _optional = False

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    @classmethod
    def _validate(cls, value: Union[bytes, list]) -> list[bytes]:
        """Ensure an list is always returned.

        Due to the way that pydantic does validation the
        method will never be called if value is None.
        """
        # Coerce provided value to list type if required
        if not isinstance(value, list):
            return [value]

        # validate data if type is not Optional
        if cls._optional is False:
            array_validator(value)

        # TODO: [med] should content be validated to be bytes?
        return cls(value)
