"""GroupAttribute / GroupAttributes Object"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.group_attributes.group_attribute_filter import GroupAttributeFilter
from tcex.api.tc.v3.group_attributes.group_attribute_model import (
    GroupAttributeModel,
    GroupAttributesModel,
)
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class GroupAttributes(ObjectCollectionABC):
    """GroupAttributes Collection.

    # Example of params input
    {
        'result_limit': 100,  # Limit the retrieved results.
        'result_start': 10,  # Starting count used for pagination.
        'fields': ['caseId', 'summary']  # Select additional return fields.
    }

    Args:
        session (Session): Session object configured with TC API Auth.
        tql_filters (list): List of TQL filters.
        params (dict): Additional query params (see example above).
    """

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = GroupAttributesModel(**kwargs)
        self.type_ = 'group_attributes'

    def __iter__(self) -> 'GroupAttribute':
        """Iterate over CM objects."""
        return self.iterate(base_class=GroupAttribute)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.GROUP_ATTRIBUTES.value

    @property
    def filter(self) -> 'GroupAttributeFilter':
        """Return the type specific filter object."""
        return GroupAttributeFilter(self.tql)


class GroupAttribute(ObjectABC):
    """GroupAttributes Object.

    Args:
        default (bool, kwargs): A flag indicating that this is the default attribute of its type
            within the object. Only applies to certain attribute and data types.
        group_id (int, kwargs): Group associated with attribute.
        source (str, kwargs): The attribute source.
        type (str, kwargs): The attribute type.
        value (str, kwargs): Attribute value.
    """

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = GroupAttributeModel(**kwargs)
        self._nested_field_name = 'attributes'
        self._nested_filter = 'has_group_attribute'
        self.type_ = 'Group Attribute'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.GROUP_ATTRIBUTES.value

    @property
    def model(self) -> 'GroupAttributeModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['GroupAttributeModel', dict]):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')
