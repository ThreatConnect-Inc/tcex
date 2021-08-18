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
    def is_null_member(cls, value: Any) -> bool:
        """Extend basic null member check with checks specific to TCEntity.

        On top of the is_null_member check in Array parent class, a TCEntity is considered null
        when its 'value' key is None.
        """
        return (
            super().is_null_member(value) or cls.is_array_member(value) and value['value'] is None
        )

    @classmethod
    def is_empty_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        An empty member of TCEntityArray is a value that passes the checks defined in
        TCEntityArray.is_array_member and whose 'value' key maps to an empty string.
        """
        # use explicit checks for '' to circumvent ambiguity caused by other falsy values
        return cls.is_array_member(value) and value is not None and value['value'] == ''

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        A member of TCEntityArray is a dictionary that must contain 'id', 'type', and 'value' keys.
        Additionally, the 'type' and 'id' keys should always map to a non-empty string.

        The 'value' key is checked to be either an empty string or None.  The check for an empty
        'value' key is performed in is_empty_member. The check for a null 'value' key is performed
        in is_null_member.
        """
        is_array_member = True
        required_keys = ['type', 'value', 'id']

        if value is None:
            return True

        if isinstance(value, dict):
            if len(value.keys()) != len(required_keys):
                is_array_member = False

            for key in required_keys:
                if key not in value:
                    is_array_member = False

                key_value = value.get(key)

                if key == 'value':
                    # 'value' key must map to a string or None
                    if not isinstance(key_value, (str, type(None))):
                        is_array_member = False
                else:
                    # other keys must map to non-empty strings
                    if not isinstance(key_value, str) or key_value == '':
                        is_array_member = False
        else:
            # anything not a dictionary cannot be a member of TCEntityArray
            is_array_member = False

        return is_array_member


class TCEntityArrayOptional(TCEntityArray):
    """TCEntityArrayOptional Field Type"""

    _optional = True
