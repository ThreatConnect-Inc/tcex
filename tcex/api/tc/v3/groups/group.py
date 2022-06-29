"""Group / Groups Object"""
# standard library
import json
from typing import TYPE_CHECKING, Iterator, Optional, Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.group_attributes.group_attribute_model import GroupAttributeModel
from tcex.api.tc.v3.groups.group_filter import GroupFilter
from tcex.api.tc.v3.groups.group_model import GroupModel, GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelModel
from tcex.api.tc.v3.tags.tag_model import TagModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetModel

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from requests import Response

    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact
    from tcex.api.tc.v3.cases.case import Case
    from tcex.api.tc.v3.group_attributes.group_attribute import GroupAttribute
    from tcex.api.tc.v3.indicators.indicator import Indicator
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel
    from tcex.api.tc.v3.tags.tag import Tag
    from tcex.api.tc.v3.victim_assets.victim_asset import VictimAsset


class Groups(ObjectCollectionABC):
    """Groups Collection.

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
        self._model = GroupsModel(**kwargs)
        self.type_ = 'groups'

    def __iter__(self) -> 'Group':
        """Iterate over CM objects."""
        return self.iterate(base_class=Group)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.GROUPS.value

    @property
    def filter(self) -> 'GroupFilter':
        """Return the type specific filter object."""
        return GroupFilter(self.tql)


class Group(ObjectABC):
    """Groups Object.

    Args:
        assignments (TaskAssignees, kwargs): A list of assignees and escalatees associated with this
            group (Task specific).
        associated_artifacts (Artifacts, kwargs): A list of Artifacts associated with this Group.
        associated_cases (Cases, kwargs): A list of Cases associated with this Group.
        associated_groups (Groups, kwargs): A list of groups associated with this group.
        associated_indicators (Indicators, kwargs): A list of indicators associated with this group.
        associated_victim_assets (VictimAssets, kwargs): A list of victim assets associated with
            this group.
        attributes (GroupAttributes, kwargs): A list of Attributes corresponding to the Group.
        body (str, kwargs): The email Body.
        due_date (str, kwargs): The date and time that the Task is due.
        escalation_date (str, kwargs): The escalation date and time.
        event_date (str, kwargs): The date and time that the incident or event was first created.
        file_name (str, kwargs): The document or signature file name.
        file_text (str, kwargs): The signature file text.
        file_type (str, kwargs): The signature file type.
        first_seen (str, kwargs): The date and time that the campaign was first created.
        from_ (str, kwargs): The email From field.
        header (str, kwargs): The email Header field.
        malware (bool, kwargs): Is the document malware?
        name (str, kwargs): The name of the group.
        password (str, kwargs): The password associated with the document (Required if Malware is
            true).
        publish_date (str, kwargs): The date and time that the report was first created.
        reminder_date (str, kwargs): The reminder date and time.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified).
        status (str, kwargs): The status associated with this document, event, task, or incident
            (read only for task, document, and report).
        subject (str, kwargs): The email Subject section.
        tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this parameter
            will replace any existing tag(s) with the one(s) specified).
        type (str, kwargs): The **type** for the Group.
        xid (str, kwargs): The xid of the item.
    """

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = GroupModel(**kwargs)
        self._nested_field_name = 'associatedGroups'
        self._nested_filter = 'has_group'
        self.type_ = 'Group'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.GROUPS.value

    @property
    def model(self) -> 'GroupModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['GroupModel', dict]):
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
        type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.name}

    def remove(self, params: Optional[dict] = None):
        """Remove a nested object."""
        method = 'PUT'
        unique_id = self._calculate_unique_id()

        # validate an id is available
        self._validate_id(unique_id.get('value'), '')

        body = json.dumps(
            {
                self._nested_field_name: {
                    'data': [{unique_id.get('filter'): unique_id.get('value')}],
                    'mode': 'delete',
                }
            }
        )

        # get the unique id value for id, xid, summary, etc ...
        parent_api_endpoint = self._parent_data.get('api_endpoint')
        parent_unique_id = self._parent_data.get('unique_id')
        url = f'{parent_api_endpoint}/{parent_unique_id}'

        # validate parent an id is available
        self._validate_id(parent_unique_id, url)

        self._request(
            method=method,
            url=url,
            body=body,
            headers={'content-type': 'application/json'},
            params=params,
        )

        return self.request

    def download(self, params: Optional[dict] = None) -> bytes:
        """Return the document attachment for Document/Report Types."""
        self._request(
            method='GET',
            url=f'''{self.url('GET')}/download''',
            # headers={'content-type': 'application/octet-stream'},
            headers=None,
            params=params,
        )
        return self.request.content

    def pdf(self, params: Optional[dict] = None) -> bytes:
        """Return the document attachment for Document/Report Types."""
        self._request(
            method='GET',
            body=None,
            url=f'''{self.url('GET')}/pdf''',
            headers=None,
            params=params,
        )

        return self.request.content

    def upload(self, content: Union[bytes, str], params: Optional[dict] = None) -> 'Response':
        """Return the document attachment for Document/Report Types."""
        self._request(
            method='POST',
            url=f'''{self.url('GET')}/upload''',
            body=content,
            headers={'content-type': 'application/octet-stream'},
            params=params,
        )
        return self.request

    @property
    def associated_artifacts(self) -> Iterator['Artifact']:
        """Yield Artifact from Artifacts."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact import Artifacts

        yield from self._iterate_over_sublist(Artifacts)

    @property
    def associated_cases(self) -> Iterator['Case']:
        """Yield Case from Cases."""
        # first-party
        from tcex.api.tc.v3.cases.case import Cases

        yield from self._iterate_over_sublist(Cases)

    @property
    def associated_groups(self) -> Iterator['Group']:
        """Yield Group from Groups."""
        # Ensure the current item is not returned as a association
        for group in self._iterate_over_sublist(Groups):
            if group.model.id == self.model.id:
                continue
            yield group

    @property
    def associated_indicators(self) -> Iterator['Indicator']:
        """Yield Indicator from Indicators."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator import Indicators

        yield from self._iterate_over_sublist(Indicators)

    @property
    def associated_victim_assets(self) -> Iterator['VictimAsset']:
        """Yield Victim_Asset from Victim_Assets."""
        # first-party
        from tcex.api.tc.v3.victim_assets.victim_asset import VictimAssets

        yield from self._iterate_over_sublist(VictimAssets)

    @property
    def attributes(self) -> Iterator['GroupAttribute']:
        """Yield Attribute from Attributes."""
        # first-party
        from tcex.api.tc.v3.group_attributes.group_attribute import GroupAttributes

        yield from self._iterate_over_sublist(GroupAttributes)

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

    def stage_associated_case(self, data: Union[dict, 'ObjectABC', 'CaseModel']):
        """Stage case on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = CaseModel(**data)

        if not isinstance(data, CaseModel):
            raise RuntimeError('Invalid type passed in to stage_associated_case')
        data._staged = True
        self.model.associated_cases.data.append(data)

    def stage_associated_artifact(self, data: Union[dict, 'ObjectABC', 'ArtifactModel']):
        """Stage artifact on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = ArtifactModel(**data)

        if not isinstance(data, ArtifactModel):
            raise RuntimeError('Invalid type passed in to stage_associated_artifact')
        data._staged = True
        self.model.associated_artifacts.data.append(data)

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

    def stage_associated_victim_asset(self, data: Union[dict, 'ObjectABC', 'VictimAssetModel']):
        """Stage victim_asset on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = VictimAssetModel(**data)

        if not isinstance(data, VictimAssetModel):
            raise RuntimeError('Invalid type passed in to stage_associated_victim_asset')
        data._staged = True
        self.model.assets.data.append(data)

    def stage_associated_indicator(self, data: Union[dict, 'ObjectABC', 'IndicatorModel']):
        """Stage indicator on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = IndicatorModel(**data)

        if not isinstance(data, IndicatorModel):
            raise RuntimeError('Invalid type passed in to stage_associated_indicator')
        data._staged = True
        self.model.associated_indicators.data.append(data)

    def stage_attribute(self, data: Union[dict, 'ObjectABC', 'GroupAttributeModel']):
        """Stage attribute on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = GroupAttributeModel(**data)

        if not isinstance(data, GroupAttributeModel):
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
