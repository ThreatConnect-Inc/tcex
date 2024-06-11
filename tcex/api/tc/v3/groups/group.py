"""TcEx Framework Module"""

# standard library
import json
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING, Self

# third-party
from requests import Response

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
    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.cases.case import Case  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.group_attributes.group_attribute import GroupAttribute  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.indicators.indicator import Indicator  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.tags.tag import Tag  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.victim_assets.victim_asset import VictimAsset  # CIRCULAR-IMPORT


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
        event_type (str, kwargs): The identification of an event type.
        external_date_added (str, kwargs): The date and time that the item was first created
            externally.
        external_date_expires (str, kwargs): The date and time the item expires externally.
        external_last_modified (str, kwargs): The date and time the item was modified externally.
        file_name (str, kwargs): The document or signature file name.
        file_text (str, kwargs): The signature file text.
        file_type (str, kwargs): The signature file type.
        first_seen (str, kwargs): The date and time that the item was first seen.
        from_ (str, kwargs): The email From field.
        header (str, kwargs): The email Header field.
        last_seen (str, kwargs): The date and time that the item was last seen.
        malware (bool, kwargs): Is the document malware?
        name (str, kwargs): The name of the group.
        owner_id (int, kwargs): The id of the Organization, Community, or Source that the item
            belongs to.
        owner_name (str, kwargs): The name of the Organization, Community, or Source that the item
            belongs to.
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
        up_vote (bool, kwargs): Is the intelligence valid and useful? (0 means downvote, 1 means
            upvote, and NULL means no vote).
        xid (str, kwargs): The xid of the item.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: GroupModel = GroupModel(**kwargs)
        self._nested_field_name = 'associatedGroups'
        self._nested_filter = 'has_group'
        self.type_ = 'Group'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.GROUPS.value

    @property
    def model(self) -> GroupModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | GroupModel):
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

    def remove(self, params: dict | None = None):
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

    def download(self, params: dict | None = None) -> bytes:
        """Return the document attachment for Document/Report Types."""
        self._request(
            method='GET',
            url=f'''{self.url('GET')}/download''',
            headers={'Accept': 'application/octet-stream'},
            params=params,
        )
        return self.request.content

    def pdf(self, params: dict | None = None) -> bytes:
        """Return the document attachment for Document/Report Types."""
        self._request(
            method='GET',
            body=None,
            url=f'''{self.url('GET')}/pdf''',
            headers={'Accept': 'application/octet-stream'},
            params=params,
        )

        return self.request.content

    def upload(self, content: bytes | str, params: dict | None = None) -> Response:
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
    def associated_artifacts(self) -> Generator['Artifact', None, None]:
        """Yield Artifact from Artifacts."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact import Artifacts

        yield from self._iterate_over_sublist(Artifacts)  # type: ignore

    @property
    def associated_cases(self) -> Generator['Case', None, None]:
        """Yield Case from Cases."""
        # first-party
        from tcex.api.tc.v3.cases.case import Cases

        yield from self._iterate_over_sublist(Cases)  # type: ignore

    @property
    def associated_groups(self) -> Generator[Self, None, None]:
        """Yield Group from Groups."""
        # Ensure the current item is not returned as a association
        for group in self._iterate_over_sublist(Groups):  # type: ignore
            if group.model.id == self.model.id:
                continue
            yield group  # type: ignore

    @property
    def associated_indicators(self) -> Generator['Indicator', None, None]:
        """Yield Indicator from Indicators."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator import Indicators

        yield from self._iterate_over_sublist(Indicators)  # type: ignore

    @property
    def associated_victim_assets(self) -> Generator['VictimAsset', None, None]:
        """Yield VictimAsset from VictimAssets."""
        # first-party
        from tcex.api.tc.v3.victim_assets.victim_asset import VictimAssets

        yield from self._iterate_over_sublist(VictimAssets)  # type: ignore

    @property
    def attributes(self) -> Generator['GroupAttribute', None, None]:
        """Yield Attribute from Attributes."""
        # first-party
        from tcex.api.tc.v3.group_attributes.group_attribute import GroupAttributes

        yield from self._iterate_over_sublist(GroupAttributes)  # type: ignore

    @property
    def security_labels(self) -> Generator['SecurityLabel', None, None]:
        """Yield SecurityLabel from SecurityLabels."""
        # first-party
        from tcex.api.tc.v3.security_labels.security_label import SecurityLabels

        yield from self._iterate_over_sublist(SecurityLabels)  # type: ignore

    @property
    def tags(self) -> Generator['Tag', None, None]:
        """Yield Tag from Tags."""
        # first-party
        from tcex.api.tc.v3.tags.tag import Tags

        yield from self._iterate_over_sublist(Tags)  # type: ignore

    def stage_associated_case(self, data: dict | ObjectABC | CaseModel):
        """Stage case on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = CaseModel(**data)

        if not isinstance(data, CaseModel):
            raise RuntimeError('Invalid type passed in to stage_associated_case')
        data._staged = True
        self.model.associated_cases.data.append(data)  # type: ignore

    def stage_associated_artifact(self, data: dict | ObjectABC | ArtifactModel):
        """Stage artifact on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = ArtifactModel(**data)

        if not isinstance(data, ArtifactModel):
            raise RuntimeError('Invalid type passed in to stage_associated_artifact')
        data._staged = True
        self.model.associated_artifacts.data.append(data)  # type: ignore

    def stage_associated_group(self, data: dict | ObjectABC | GroupModel):
        """Stage group on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = GroupModel(**data)

        if not isinstance(data, GroupModel):
            raise RuntimeError('Invalid type passed in to stage_associated_group')
        data._staged = True
        self.model.associated_groups.data.append(data)  # type: ignore

    def stage_associated_victim_asset(self, data: dict | ObjectABC | VictimAssetModel):
        """Stage victim_asset on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = VictimAssetModel(**data)

        if not isinstance(data, VictimAssetModel):
            raise RuntimeError('Invalid type passed in to stage_associated_victim_asset')
        data._staged = True
        self.model.associated_victim_assets.data.append(data)  # type: ignore

    def stage_associated_indicator(self, data: dict | ObjectABC | IndicatorModel):
        """Stage indicator on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = IndicatorModel(**data)

        if not isinstance(data, IndicatorModel):
            raise RuntimeError('Invalid type passed in to stage_associated_indicator')
        data._staged = True
        self.model.associated_indicators.data.append(data)  # type: ignore

    def stage_attribute(self, data: dict | ObjectABC | GroupAttributeModel):
        """Stage attribute on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = GroupAttributeModel(**data)

        if not isinstance(data, GroupAttributeModel):
            raise RuntimeError('Invalid type passed in to stage_attribute')
        data._staged = True
        self.model.attributes.data.append(data)  # type: ignore

    def stage_security_label(self, data: dict | ObjectABC | SecurityLabelModel):
        """Stage security_label on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = SecurityLabelModel(**data)

        if not isinstance(data, SecurityLabelModel):
            raise RuntimeError('Invalid type passed in to stage_security_label')
        data._staged = True
        self.model.security_labels.data.append(data)  # type: ignore

    def stage_tag(self, data: dict | ObjectABC | TagModel):
        """Stage tag on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = TagModel(**data)

        if not isinstance(data, TagModel):
            raise RuntimeError('Invalid type passed in to stage_tag')
        data._staged = True
        self.model.tags.data.append(data)  # type: ignore


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
        """Initialize instance properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = GroupsModel(**kwargs)
        self.type_ = 'groups'

    def __iter__(self) -> Iterator[Group]:
        """Return CM objects."""
        return self.iterate(base_class=Group)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.GROUPS.value

    @property
    def filter(self) -> GroupFilter:
        """Return the type specific filter object."""
        return GroupFilter(self.tql)
