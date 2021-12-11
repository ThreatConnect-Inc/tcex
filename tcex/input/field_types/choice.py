"""Sensitive Field Type"""
# TODO: [high] update docstrings
# standard library
import logging
from typing import Any, Callable

# get tcex logger
logger = logging.getLogger('tcex')


class Choice:
    """Field Type to hold sensitive data."""

    def __init__(self, value):
        """Initialize choice type"""
        if isinstance(value, Choice):
            self._value = value.value
        else:
            self._value = value

    @property
    def value(self) -> str:
        """Return the selection. Return None if selection is '-- Select --'"""
        return None if self._value == '-- Select --' else self._value

    @classmethod
    def __get_validators__(cls) -> Callable:
        """Define one or more validators for Pydantic custom type."""
        yield cls._validate

    @classmethod
    def _validate(cls, value: Any) -> 'Choice':
        """Pydantic validate method."""
        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise ValueError(f'Choice Type expects String values, received: {type(value)}')

        if value == '':
            raise ValueError('Choice value may not be empty.')

        return cls(value)
