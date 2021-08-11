"""TCEntityArray Types"""
# standard library
from typing import Any

from .array_abc import AbstractEntityArray


class TCEntityArray(AbstractEntityArray):
    """TCEntityArray Field Type"""

    # TODO: [high] this could be an issue as KeyValueArray will also come in from KeyValueList
    __input_type__ = 'String'
    __playbook_data_type__ = ['TCEntity', 'TCEntityArray']
    _optional = False

    @classmethod
    def is_empty_member(cls, value: Any):
        """Implement abstract method in Array parent class.

        An empty member of TCEntityArray is a value that passes the checks defined in
        TCEntityArray.is_array_member and whose 'value' key maps to an empty string or to None.
        """
        # use explicit checks for None and '' to circumvent ambiguity caused by other falsy values
        return cls.is_array_member(value) and (value['value'] is None or value['value'] == '')

    @classmethod
    def is_array_member(cls, value: Any):
        """Implement abstract method in Array parent class.

        A member of TCEntityArray is a dictionary that must contain 'type' and 'value' keys.
        The 'id' key is not explicitly checked for, as Attribute TCEntities do not have it.
        Additionally, the 'type' key should always map to a non-empty string.
        """
        required_keys = ['type', 'value']
        return (
            isinstance(value, dict)
            and all([key in value for key in required_keys])
            and isinstance(value['type'], str)
            and value['type'] != ''
        )


class TCEntityArrayOptional(TCEntityArray):
    """TCEntityArrayOptional Field Type"""

    _optional = True
