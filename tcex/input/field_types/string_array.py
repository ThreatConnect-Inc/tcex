"""StringArray Types"""
# standard library
from typing import Any

from .array_abc import AbstractArray


class StringArray(AbstractArray):
    """StringArray Field Type"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['String', 'StringArray']

    @classmethod
    def is_empty_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        An empty member of StringArray is ''
        """
        return value == ''

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        A member of StringArray is a string instance
        """
        return isinstance(value, str)


class StringArrayOptional(StringArray):
    """StringArrayOptional Field Type"""

    _optional = True
