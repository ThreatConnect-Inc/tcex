"""Owner / Owners Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.owners.owner_filter import OwnerFilter
from tcex.api.tc.v3.security.owners.owner_model import OwnerModel, OwnersModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator


class Owners(ObjectCollectionABC):
    """Owners Collection.

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
        self._model = OwnersModel(**kwargs)
        self._type = 'owners'

    def __iter__(self) -> 'Owner':
        """Iterate over CM objects."""
        return self.iterate(base_class=Owner)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.OWNERS.value

    @property
    def filter(self) -> 'OwnerFilter':
        """Return the type specific filter object."""
        return OwnerFilter(self.tql)


class Owner(ObjectABC):
    """Owners Object."""

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = OwnerModel(**kwargs)
        self._type = 'owner'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.OWNERS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'owner_id',
            'operator': TqlOperator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        return {'type': 'Owner', 'id': self.model.id, 'value': self.model.summary}
