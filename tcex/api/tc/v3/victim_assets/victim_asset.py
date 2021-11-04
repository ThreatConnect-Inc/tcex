"""VictimAsset / VictimAssets Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.victim_assets.victim_asset_filter import VictimAssetFilter
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetModel, VictimAssetsModel


class VictimAssets(ObjectCollectionABC):
    """VictimAssets Collection.

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
        self._model = VictimAssetsModel(**kwargs)
        self._type = 'victim_assets'

    def __iter__(self) -> 'VictimAsset':
        """Iterate over CM objects."""
        return self.iterate(base_class=VictimAsset)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ASSETS.value

    @property
    def filter(self) -> 'VictimAssetFilter':
        """Return the type specific filter object."""
        return VictimAssetFilter(self.tql)


class VictimAsset(ObjectABC):
    """VictimAssets Object.

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
        self._model = VictimAssetModel(**kwargs)
        self.type_ = 'Victim Asset'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ASSETS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'victim_asset_id',
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

