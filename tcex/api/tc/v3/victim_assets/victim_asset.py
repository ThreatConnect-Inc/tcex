"""TcEx Framework Module"""

from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.victim_assets.victim_asset_filter import VictimAssetFilter
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetModel, VictimAssetsModel

if TYPE_CHECKING:  # pragma: no cover
    from tcex.api.tc.v3.groups.group import Group  # CIRCULAR-IMPORT


class VictimAsset(ObjectABC):
    """VictimAssets Object."""

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: VictimAssetModel = VictimAssetModel(**kwargs)
        self._nested_field_name = 'victimAssets'
        self._nested_filter = 'has_victim_asset'
        self.type_ = 'Victim Asset'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ASSETS.value

    @property
    def model(self) -> VictimAssetModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | VictimAssetModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            ex_msg = f'Invalid data type: {type(data)} provided.'
            raise RuntimeError(ex_msg)  # noqa: TRY004

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        value = []

        if self.model.type is not None:
            if self.model.type.lower() == 'phone':
                if self.model.phone:
                    value.append(self.model.phone)
            elif self.model.type.lower() == 'socialnetwork':
                if self.model.social_network:
                    value.append(self.model.social_network)
                if self.model.account_name:
                    value.append(self.model.account_name)
            elif self.model.type.lower() == 'networkaccount':
                if self.model.network_type:
                    value.append(self.model.network_type)
                if self.model.account_name:
                    value.append(self.model.account_name)
            elif self.model.type.lower() == 'emailaddress':
                if self.model.address_type:
                    value.append(self.model.address_type)
                if self.model.address:
                    value.append(self.model.address)
            elif self.model.type.lower() == 'website' and self.model.website:
                value.append(self.model.website)

        value = ' : '.join(value) if value else ''
        type_ = f'Victim Asset : {self.model.type}'

        return {'type': type_, 'id': self.model.id, 'value': value}

    @property
    def associated_groups(self) -> Generator['Group', None, None]:
        """Yield Group from Groups."""
        from tcex.api.tc.v3.groups.group import Groups  # noqa: PLC0415

        yield from self._iterate_over_sublist(Groups)  # type: ignore

    def stage_associated_group(self, data: dict | ObjectABC | GroupModel):
        """Stage group on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = GroupModel(**data)

        if not isinstance(data, GroupModel):
            ex_msg = 'Invalid type passed in to stage_associated_group'
            raise RuntimeError(ex_msg)  # noqa: TRY004
        data._staged = True  # noqa: SLF001
        self.model.associated_groups.data.append(data)  # type: ignore


class VictimAssets(ObjectCollectionABC):
    """VictimAssets Collection.

    # Example of params input
    {
        "result_limit": 100,  # Limit the retrieved results.
        "result_start": 10,  # Starting count used for pagination.
        "fields": ["caseId", "summary"]  # Select additional return fields.
    }

    Args:
        session (Session): Session object configured with TC API Auth.
        tql_filters (list): List of TQL filters.
        params (dict): Additional query params (see example above).
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = VictimAssetsModel(**kwargs)
        self.type_ = 'victim_assets'

    def __iter__(self) -> Iterator[VictimAsset]:
        """Return CM objects."""
        return self.iterate(base_class=VictimAsset)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIM_ASSETS.value

    @property
    def filter(self) -> VictimAssetFilter:
        """Return the type specific filter object."""
        return VictimAssetFilter(self.tql)
