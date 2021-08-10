"""Always Array Validator"""
# standard library
from typing import Any

# first-party
from .array_abc import Array


class BinaryArray(Array):
    """BinaryArray Field Type"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['Binary', 'BinaryArray']
    _optional = False

    @classmethod
    def is_empty_member(cls, value: Any):
        """Implementation of abstract method in Array parent class.

        An empty member of BinaryArray is b''
        """
        return value == b''

    @classmethod
    def is_array_member(cls, value: Any):
        """Implementation of abstract method in Array parent class.

        A member of BinaryArray is a bytes instance
        """
        return isinstance(value, bytes)


class BinaryArrayOptional(BinaryArray):
    """BinaryArrayOptional Field Type"""
    _optional = True
