"""VictimAsset / VictimAssets Object"""
# standard library
from typing import TYPE_CHECKING, Iterator, Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.victim_assets.victim_asset_filter import VictimAssetFilter
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetModel, VictimAssetsModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.groups.group import Group


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

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = VictimAssetsModel(**kwargs)
        self.type_ = 'victim_assets'

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
        account_name (str, kwargs): The network name.
        address (str, kwargs): The email address associated with the E-Mail Address asset.
        address_type (str, kwargs): The type of the E-Mail Address asset.
        associated_groups (Groups, kwargs): A list of groups that this victim asset is associated
            with.
        network_type (str, kwargs): The type of network.
        phone (str, kwargs): The phone number of the asset.
        social_network (str, kwargs): The type of social network.
        type (str, kwargs): Type of victim asset.
        victim_id (int, kwargs): Victim id of victim asset.
        website (str, kwargs): The website of the asset.
    """

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = VictimAssetModel(**kwargs)
        self._nested_field_name = 'victimAssets'
        self._nested_filter = 'has_victim_asset'
        self.type_ = 'Victim Asset'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ASSETS.value

    @property
    def model(self) -> 'VictimAssetModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['VictimAssetModel', dict]):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    @property
    def associated_groups(self) -> Iterator['Group']:
        """Yield Group from Groups."""
        # first-party
        from tcex.api.tc.v3.groups.group import Groups

        yield from self._iterate_over_sublist(Groups)

    def stage_associated_group(self, data: Union[dict, 'ObjectABC', 'GroupModel']):
        """Stage group on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = GroupModel(**data)

        if not isinstance(data, GroupModel):
            raise RuntimeError('Invalid type passed in to stage_associated_group')
        data._staged = True
        self.model.associated_groups.data.append(data)
