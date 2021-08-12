"""IndicatorArray Types"""
# standard library
from typing import Any, Union

# first-party
from tcex.input.field_types import StringArray, TCEntityArray
from tcex.input.field_types.hybrid_array_abc import AbstractHybridArray
from tcex.input.field_types.utils import ti_utils


class IndicatorArray(AbstractHybridArray):
    """IndicatorArray Field Type

    This type is a hybrid type of StringArray and TCEntityArray. This means that IndicatorArray
    may hold both String and TCEntity types.
    """

    __input_type__ = 'String'
    __playbook_data_type__ = ['String', 'StringArray', 'TCEntity', 'TCEntityArray']

    @classmethod
    def _type_compositions(cls) -> list[Union[StringArray, TCEntityArray]]:
        """Implement abstract method in Array parent class.

        IndicatorArray is a HybridArray composed of StringArray and TCEntityArray.
        """
        return [StringArray, TCEntityArray]

    @classmethod
    def is_array_member(cls, value: Any) -> bool:
        """Extend HybridArray is_array_member implementation.

        In addition to passing the checks provided in AbstractHybridArray.is_array_member, a value
        must also contain a 'type' key that is one of the valid indicator types (if value is a
        TCEntity) in order to be considered a member of IndicatorArray.
        """
        # ensure value is a valid member of StringArray or TCEntityArray
        is_member = super().is_array_member(value)

        return is_member and (
            # ensure type is an indicator type if value is TCEntity
            isinstance(value, str)
            or value.get('type') in ti_utils().indicator_types
        )


class IndicatorArrayOptional(IndicatorArray):
    """Optional IndicatorArray Field Types."""

    _optional = True
