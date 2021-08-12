"""GroupArray Types"""
# standard library
from typing import Any

# first-party
from tcex.input.field_types.intel_array import IntelArray
from tcex.input.field_types.utils import ti_utils


class GroupArray(IntelArray):
    """GroupArray Field Type

    This type is a descendant of IntelArray. This means that GroupArray is a HybridArray that
    may hold both String and TCEntity types as IntelArray does, except that GroupArray
    further checks that TCEntities have a 'type' that is a valid Group type.
    """

    __input_type__ = 'String'
    __playbook_data_type__ = ['String', 'StringArray', 'TCEntity', 'TCEntityArray']

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Extend HybridArray is_array_member implementation.

        In addition to passing the checks provided in AbstractHybridArray.is_array_member, a value
        must also contain a 'type' key that is one of the valid Group types (if value is a
        TCEntity) in order to be considered a member of GroupArray.
        """
        # ensure value is a valid member of StringArray or TCEntityArray
        is_member = super().is_array_member(value)

        return is_member and (
            # ensure type is a Group type if value is TCEntity
            isinstance(value, str)
            or value.get('type') in ti_utils().group_types
        )


class GroupArrayOptional(GroupArray):
    """Optional GroupArray Field Type"""

    _optional = True
