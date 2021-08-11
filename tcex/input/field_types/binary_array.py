"""BinaryArray Types"""
# standard library
from typing import Any

from .array_abc import AbstractArray


class BinaryArray(AbstractArray):
    """BinaryArray Field Type"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['Binary', 'BinaryArray']
    _optional = False

    @classmethod
    def is_empty_member(cls, value: Any):
        """Implement abstract method in Array parent class.

        An empty member of BinaryArray is b''
        """
        return value == b''

    @classmethod
    def is_array_member(cls, value: Any):
        """Implement abstract method in Array parent class.

        A member of BinaryArray is a bytes instance
        """
        return isinstance(value, bytes)


class BinaryArrayOptional(BinaryArray):
    """BinaryArrayOptional Field Type"""

    _optional = True
