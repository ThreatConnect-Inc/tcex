"""AdversaryAsset / AdversaryAssets Object"""
# first-party
from tcex.api.tc.v3.adversary_assets.adversary_asset_filter import AdversaryAssetFilter
from tcex.api.tc.v3.adversary_assets.adversary_asset_model import (
    AdversaryAssetModel,
    AdversaryAssetsModel,
)
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tql.tql_operator import TqlOperator


class AdversaryAssets(ObjectCollectionABC):
    """AdversaryAssets Collection.

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
        self._model = AdversaryAssetsModel(**kwargs)
        self._type = 'adversary_assets'

    def __iter__(self) -> 'AdversaryAsset':
        """Iterate over CM objects."""
        return self.iterate(base_class=AdversaryAsset)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ADVERSARY_ASSETS.value

    @property
    def filter(self) -> 'AdversaryAssetFilter':
        """Return the type specific filter object."""
        return AdversaryAssetFilter(self.tql)


class AdversaryAsset(ObjectABC):
    """AdversaryAssets Object.

    Args:
        associated_groups (Groups, kwargs): A list of groups that this victim asset is associated
            with.
        name (str, kwargs): Name of victim asset.
        type (str, kwargs): Type of victim asset.
        victim_id (int, kwargs): Victim id of victim asset.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = AdversaryAssetModel(**kwargs)
        self._type = 'adversary_asset'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ADVERSARY_ASSETS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'adversary_asset_id',
            'operator': TqlOperator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        return {'type': 'AdversaryAsset', 'id': self.model.id, 'value': self.model.summary}
