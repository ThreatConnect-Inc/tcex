"""VictimAttribute / VictimAttributes Object"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.victim_attributes.victim_attribute_filter import VictimAttributeFilter
from tcex.api.tc.v3.victim_attributes.victim_attribute_model import (
    VictimAttributeModel,
    VictimAttributesModel,
)


class VictimAttributes(ObjectCollectionABC):
    """VictimAttributes Collection.

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
        self._model = VictimAttributesModel(**kwargs)
        self.type_ = 'victim_attributes'

    def __iter__(self) -> 'VictimAttribute':
        """Iterate over CM objects."""
        return self.iterate(base_class=VictimAttribute)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ATTRIBUTES.value

    @property
    def filter(self) -> 'VictimAttributeFilter':
        """Return the type specific filter object."""
        return VictimAttributeFilter(self.tql)


class VictimAttribute(ObjectABC):
    """VictimAttributes Object.

    Args:
        default (bool, kwargs): A flag indicating that this is the default attribute of its type
            within the object. Only applies to certain attribute and data types.
        source (str, kwargs): The attribute source.
        type (str, kwargs): The attribute type.
        value (str, kwargs): Attribute value.
        victim_id (int, kwargs): Victim associated with attribute.
    """

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = VictimAttributeModel(**kwargs)
        self._nested_field_name = 'victimAttributes'
        self._nested_filter = 'has_victim_attribute'
        self.type_ = 'Victim Attribute'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ATTRIBUTES.value

    @property
    def model(self) -> 'VictimAttributeModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['VictimAttributeModel', dict]):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')
