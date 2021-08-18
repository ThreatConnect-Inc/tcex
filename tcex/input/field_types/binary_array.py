"""BinaryArray Types"""
# standard library
from typing import Any

from .array_abc import AbstractArray


class BinaryArray(AbstractArray):
    """BinaryArray Field Type"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['Binary', 'BinaryArray']

    @classmethod
    def is_empty_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        An empty member of BinaryArray is b''
        """
        cls.assert_is_member(value)
        return value == b''

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        A member of BinaryArray is a bytes instance or None
        """
        return isinstance(value, (bytes, type(None)))


class BinaryArrayOptional(BinaryArray):
    """BinaryArrayOptional Field Type"""

    _optional = True
