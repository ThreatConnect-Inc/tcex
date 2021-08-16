"""KeyValueArray Types"""
# standard library
from typing import Any

# first-party
from tcex.input.field_types.binary_array import BinaryArray
from tcex.input.field_types.string_array import StringArray
from tcex.input.field_types.tc_entity_array import TCEntityArray

from .array_abc import AbstractArray
from .exception import HeterogenousArrayException, InvalidMemberException


class KeyValueArray(AbstractArray):
    """KeyValueArray Field Type"""

    __input_type__ = 'String'
    __playbook_data_type__ = ['KeyValue', 'KeyValueArray']
    _optional = False

    @classmethod
    def is_empty_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        An empty member of KeyValueArray is a value that passes the checks defined in
        KeyValueArray.is_array_member and either is None, or is a KeyValue that has a 'value' that
        is None, an empty list, or is considered to be an empty member of StringArray or
        BinaryArray.

        If the passed-in value is a KeyValue whose 'value' is another KeyValue or a TCEntity,
        the KeyValue/TCEntity found in the 'value' portion are not checked for emptiness. The
        passed-in KeyValue is considered non-empty in these cases.
        """
        is_member = cls.is_array_member(value)

        if is_member:
            if value is None:
                return True

            key_value = value.get('value')
            # 'value' of KeyValue is set to None or empty list
            if key_value in [None, []]:
                return True

            # 'value' of KeyValue is set to empty member of StringArray or BinaryArray
            other_allowed_types = [StringArray, BinaryArray]
            if any(_type.is_empty_member(key_value) for _type in other_allowed_types):
                return True
        else:
            return False

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Implement abstract method in Array parent class.

        A member of KeyValueArray is a dictionary that has 'key' and 'value' keys. An optional
        'variableType' key may be included, which must be a non-empty string if present.

        The 'key' key must be a non-empty string.

        The 'value' key may be a String, StringArray, Binary, BinaryArray, TCEntity, TCEntityArray,
        and it also may be another KeyValue or a KeyValueArray. Note that this means that the value
        may be a single value or a list (Array) type. If the 'value' key is a list type, then
        it must be a homogenous list. That is, the list may contain only Strings, only Binaries,
        only TCEntities, or only KeyValues.

        The 'value' key may also be None.
        """
        required_keys = ['key', 'value']
        optional_keys = ['variableType']

        # can be None
        if value is None:
            return True

        # KeyValue is always a dictionary
        if not isinstance(value, dict):
            return False

        # KeyValue dictionary must contain required keys
        if not all(key in value for key in required_keys):
            return False

        keys = value.keys()
        # additional keys found
        if not len(keys) == len(required_keys):
            other_keys = [key for key in keys if key not in required_keys]
            # additional keys must be part of optional_keys
            if not all(key in optional_keys for key in other_keys):
                return False

        key = value.get('key')
        key_value = value.get('value')

        # 'key' part of KeyValue must be a non-empty string
        if not isinstance(key, str) or key == '':
            return False

        # 'value' part of KeyValue is an Array (list)
        if cls.is_array(key_value):
            # should contain String, Binary, TCEntity, or KeyValues. 'value' cannot be list of lists
            if any([isinstance(item, list) for item in key_value]):
                return False

            # should be homogenous (add 'cls' because 'value' could be a list of KeyValues)
            for _type in [StringArray, BinaryArray, TCEntityArray, cls]:
                try:
                    _type.assert_homogenous(key_value)
                except HeterogenousArrayException:
                    # 'value' part of KeyValue is not homogenous array of current _type
                    pass
                else:
                    # No exception was raised, must be homogenous list of current _type
                    return True
            else:
                # was not homogenous array of any of the accepted types
                return False
        # 'value' part of KeyValue is a single value.
        else:
            # 'value' part of KeyValue is allowed to be None
            if key_value is None:
                return True

            # should be a single String, Binary, TCEntity, or KeyValue
            for _type in [StringArray, BinaryArray, TCEntityArray, cls]:
                try:
                    _type.assert_is_member(key_value)
                except InvalidMemberException:
                    # 'value' part of KeyValue is not a member of current _type
                    pass
                else:
                    # No exception was raised, must be a member of current _type
                    return True
            else:
                # was not member of any of the accepted types
                return False


class KeyValueArrayOptional(KeyValueArray):
    """KeyValueArrayOptional Field Type"""

    _optional = True
