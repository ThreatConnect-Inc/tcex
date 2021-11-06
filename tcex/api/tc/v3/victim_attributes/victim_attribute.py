"""VictimAttribute / VictimAttributes Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
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

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = VictimAttributesModel(**kwargs)
        self._type = 'victim_attributes'

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

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = VictimAttributeModel(**kwargs)
        self.type_ = 'Victim Attribute'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ATTRIBUTES.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'victim_attribute_id',
            'operator': TqlOperator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_
        if hasattr(self.model, 'type'):
            type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}
