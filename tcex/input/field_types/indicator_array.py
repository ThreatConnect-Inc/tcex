"""IndicatorArray Types"""
# standard library
from typing import Any

# first-party
from tcex.input.field_types.intel_array import IntelArray
from tcex.input.field_types.utils import ti_utils


class IndicatorArray(IntelArray):
    """IndicatorArray Field Type

    This type is a descendant of IntelArray. This means that IndicatorArray is a HybridArray that
    may hold both String and TCEntity types as IntelArray does, except that IndicatorArray
    further checks that TCEntities have a 'type' that is a valid Indicator type.
    """

    __input_type__ = 'String'
    __playbook_data_type__ = ['String', 'StringArray', 'TCEntity', 'TCEntityArray']

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Extend HybridArray is_array_member implementation.

        In addition to passing the checks provided in AbstractHybridArray.is_array_member, a value
        must also contain a 'type' key that is one of the valid Indicator types (if value is a
        TCEntity) in order to be considered a member of IndicatorArray.
        """
        # ensure value is a valid member of StringArray or TCEntityArray
        is_member = super().is_array_member(value)

        if is_member and isinstance(value, dict):
            is_member = value.get('type') in ti_utils().indicator_types

        return is_member


class IndicatorArrayOptional(IndicatorArray):
    """IndicatorArrayOptional Field Type"""

    _optional = True
