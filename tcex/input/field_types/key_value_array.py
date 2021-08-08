"""Always Array Validator"""
# standard library
from typing import Callable, Union

# first-party
from tcex.input.field_types.utils import array_validator


class KeyValueArray(str):
    """Ensure an array is always returned for the input."""

    # TODO: [high] this could be an issue as KeyValueArray will also come in from KeyValueList
    __input_type__ = 'String'
    __playbook_data_type__ = ['KeyValue', 'KeyValueArray']
    _optional = False

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    @classmethod
    def _validate(cls, value: Union[dict, list]) -> list[dict]:
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

        # TODO: [med] should content be validated for key and value fields?
        return cls(value)
