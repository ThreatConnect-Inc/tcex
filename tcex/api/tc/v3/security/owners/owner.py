"""Owner / Owners Object"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.owners.owner_filter import OwnerFilter
from tcex.api.tc.v3.security.owners.owner_model import OwnerModel, OwnersModel


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

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = OwnersModel(**kwargs)
        self.type_ = 'owners'

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

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = OwnerModel(**kwargs)
        self._nested_field_name = 'owners'
        self._nested_filter = 'has_owner'
        self.type_ = 'Owner'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.OWNERS.value

    @property
    def model(self) -> 'OwnerModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['OwnerModel', dict]):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')
