"""TCEntityArray Types"""
# standard library
from typing import Any

from .array_abc import AbstractArray


class TCEntityArray(AbstractArray):
    """TCEntityArray Field Type"""

    # TODO: [high] this could be an issue as KeyValueArray will also come in from KeyValueList
    __input_type__ = 'String'
    __playbook_data_type__ = ['TCEntity', 'TCEntityArray']

    @classmethod
    def is_empty_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        An empty member of TCEntityArray is a value that passes the checks defined in
        TCEntityArray.is_array_member and whose 'value' key maps to an empty string.
        """
        # use explicit checks for None and '' to circumvent ambiguity caused by other falsy values
        return cls.is_array_member(value) and value['value'] == ''

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        A member of TCEntityArray is a dictionary that must contain 'id', 'type', and 'value' keys.
        Additionally, the 'type' and 'id' keys should always map to a non-empty string.

        The 'value' key is not checked to be a non-empty string, as the TCEntityArray could be
        marked as optional. The check for an empty 'value' key is performed in is_empty_member.
        """
        is_array_member = True
        required_keys = ['type', 'value', 'id']

        if isinstance(value, dict):
            for key in required_keys:
                if key not in value:
                    is_array_member = False

                key_value = value.get(key)

                # value[key] must be a string
                if not isinstance(key_value, str):
                    is_array_member = False

                # value[key] must be non-empty string if key is not 'value' (could be optional)
                if key != 'value' and key_value == '':
                    is_array_member = False
        else:
            # anything not a dictionary cannot be a member of TCEntityArray
            is_array_member = False

        return is_array_member


class TCEntityArrayOptional(TCEntityArray):
    """TCEntityArrayOptional Field Type"""

    _optional = True
