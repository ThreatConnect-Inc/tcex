"""IntelArray Types"""
# standard library
from typing import List, Union

# first-party
from tcex.input.field_types.hybrid_array_abc import AbstractHybridArray
from tcex.input.field_types.string_array import StringArray
from tcex.input.field_types.tc_entity_array import TCEntityArray


class IntelArray(AbstractHybridArray):
    """IntelArray Field Type

    This type is a hybrid type of StringArray and TCEntityArray. This means that IntelArray
    may hold both String and TCEntity types.
    """

    __input_type__ = 'String'
    __playbook_data_type__ = ['String', 'StringArray', 'TCEntity', 'TCEntityArray']
    # if used, _entity_filter_types should be set to a list of group/indicator types that are
    # used to provide automatic filtering capability within the entities() method.
    _entity_filter_types = None

    @classmethod
    def type_compositions(cls) -> List[Union[StringArray, TCEntityArray]]:
        """Implement abstract method in Array parent class.

        IntelArray is a HybridArray composed of StringArray and TCEntityArray.
        """
        return [StringArray, TCEntityArray]

    def entities(self):
        """Return only TCEntity members of this HybridArray"""
        for member in self:
            if isinstance(member, dict):
                if self._entity_filter_types is not None:
                    if member.get('type') in self._entity_filter_types:
                        yield member
                else:
                    yield member

    def values(self):
        """Return String members of this HybridArray as well as 'value' key of TCEntity members"""
        for member in self:
            if isinstance(member, dict):
                yield member.get('value')
            else:
                yield member


class IntelArrayOptional(IntelArray):
    """IntelArrayOptional Field Type"""

    _optional = True
