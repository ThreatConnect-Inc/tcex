"""Always Array Modifier"""
# standard library
from typing import Any, List


def always_array(value: Any) -> List[Any]:
    """Ensure Array is always returned, even if value is not a list."""
    if value is None:
        value = []

    if not isinstance(value, list):
        value = [value]

    return value


def always_array_non_empty(value: Any) -> List[Any]:
    """Ensure Array is always returned, even if value is not a list."""
    if value in [None, '', []]:
        raise ValueError('Array must contain at least one item.')

    if not isinstance(value, list):
        value = [value]

    return value
