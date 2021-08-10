"""Always Array Validator"""
# standard library
from typing import Any

# first-party
from .array_abc import Array


class StringArray(Array):
    """StringArray Field Type"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['String', 'StringArray']
    _optional = False

    @classmethod
    def is_empty_member(cls, value: Any):
        """Implementation of abstract method in Array parent class.

        An empty member of StringArray is ''
        """
        return value == ''

    @classmethod
    def is_array_member(cls, value: Any):
        """Implementation of abstract method in Array parent class.

        A member of StringArray is a string instance
        """
        return isinstance(value, str)


class StringArrayOptional(StringArray):
    """StringArrayOptional Field Type"""
    _optional = True
