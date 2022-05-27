"""Victim / Victims Object"""
# standard library
from typing import TYPE_CHECKING, Iterator, Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelModel
from tcex.api.tc.v3.tags.tag_model import TagModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetModel
from tcex.api.tc.v3.victim_attributes.victim_attribute_model import VictimAttributeModel
from tcex.api.tc.v3.victims.victim_filter import VictimFilter
from tcex.api.tc.v3.victims.victim_model import VictimModel, VictimsModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.groups.group import Group
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel
    from tcex.api.tc.v3.tags.tag import Tag
    from tcex.api.tc.v3.victim_assets.victim_asset import VictimAsset
    from tcex.api.tc.v3.victim_attributes.victim_attribute import VictimAttribute


class Victims(ObjectCollectionABC):
    """Victims Collection.

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
        self._model = VictimsModel(**kwargs)
        self.type_ = 'victims'

    def __iter__(self) -> 'Victim':
        """Iterate over CM objects."""
        return self.iterate(base_class=Victim)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIMS.value

    @property
    def filter(self) -> 'VictimFilter':
        """Return the type specific filter object."""
        return VictimFilter(self.tql)


class Victim(ObjectABC):
    """Victims Object.

    Args:
        assets (VictimAssets, kwargs): A list of victim assets corresponding to the Victim.
        associated_groups (Groups, kwargs): A list of groups that this victim is associated with.
        attributes (VictimAttributes, kwargs): A list of Attributes corresponding to the Victim.
        name (str, kwargs): Name of the Victim.
        nationality (str, kwargs): Nationality of the Victim.
        org (str, kwargs): Org of the Victim.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified).
        suborg (str, kwargs): Suborg of the Victim.
        tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this parameter
            will replace any existing tag(s) with the one(s) specified).
        work_location (str, kwargs): Work location of the Victim.
    """

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = VictimModel(**kwargs)
        self._nested_field_name = 'victims'
        self._nested_filter = 'has_victim'
        self.type_ = 'Victim'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.VICTIMS.value

    @property
    def model(self) -> 'VictimModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['VictimModel', dict]):
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
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}

    @property
    def victim_assets(self) -> Iterator['VictimAsset']:
        """Yield Victim_Asset from Victim_Assets."""
        # first-party
        from tcex.api.tc.v3.victim_assets.victim_asset import VictimAssets

        yield from self._iterate_over_sublist(VictimAssets)

    @property
    def associated_groups(self) -> Iterator['Group']:
        """Yield Group from Groups."""
        # first-party
        from tcex.api.tc.v3.groups.group import Groups

        yield from self._iterate_over_sublist(Groups)

    @property
    def attributes(self) -> Iterator['VictimAttribute']:
        """Yield Attribute from Attributes."""
        # first-party
        from tcex.api.tc.v3.victim_attributes.victim_attribute import VictimAttributes

        yield from self._iterate_over_sublist(VictimAttributes)

    @property
    def security_labels(self) -> Iterator['SecurityLabel']:
        """Yield Security_Label from Security_Labels."""
        # first-party
        from tcex.api.tc.v3.security_labels.security_label import SecurityLabels

        yield from self._iterate_over_sublist(SecurityLabels)

    @property
    def tags(self) -> Iterator['Tag']:
        """Yield Tag from Tags."""
        # first-party
        from tcex.api.tc.v3.tags.tag import Tags

        yield from self._iterate_over_sublist(Tags)

    def stage_victim_asset(self, data: Union[dict, 'ObjectABC', 'VictimAssetModel']):
        """Stage victim_asset on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = VictimAssetModel(**data)

        if not isinstance(data, VictimAssetModel):
            raise RuntimeError('Invalid type passed in to stage_victim_asset')
        data._staged = True
        self.model.assets.data.append(data)

    def stage_attribute(self, data: Union[dict, 'ObjectABC', 'VictimAttributeModel']):
        """Stage attribute on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = VictimAttributeModel(**data)

        if not isinstance(data, VictimAttributeModel):
            raise RuntimeError('Invalid type passed in to stage_attribute')
        data._staged = True
        self.model.attributes.data.append(data)

    def stage_security_label(self, data: Union[dict, 'ObjectABC', 'SecurityLabelModel']):
        """Stage security_label on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = SecurityLabelModel(**data)

        if not isinstance(data, SecurityLabelModel):
            raise RuntimeError('Invalid type passed in to stage_security_label')
        data._staged = True
        self.model.security_labels.data.append(data)

    def stage_tag(self, data: Union[dict, 'ObjectABC', 'TagModel']):
        """Stage tag on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = TagModel(**data)

        if not isinstance(data, TagModel):
            raise RuntimeError('Invalid type passed in to stage_tag')
        data._staged = True
        self.model.tags.data.append(data)
