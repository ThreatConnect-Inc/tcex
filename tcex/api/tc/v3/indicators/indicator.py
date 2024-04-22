"""TcEx Framework Module"""

# standard library
import json
from collections.abc import Generator, Iterator
from datetime import datetime
from typing import TYPE_CHECKING, Self

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.file_actions.file_action_model import FileActionModel
from tcex.api.tc.v3.file_occurrences.file_occurrence_model import FileOccurrenceModel
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.indicator_attributes.indicator_attribute_model import IndicatorAttributeModel
from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel, IndicatorsModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelModel
from tcex.api.tc.v3.tags.tag_model import TagModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.cases.case import Case  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.groups.group import Group  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.indicator_attributes.indicator_attribute import (  # CIRCULAR-IMPORT
        IndicatorAttribute,
    )
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.tags.tag import Tag  # CIRCULAR-IMPORT


class Indicator(ObjectABC):
    """Indicators Object.

    Args:
        active (bool, kwargs): Is the indicator active?
        active_locked (bool, kwargs): Lock the indicator active value?
        address (str, kwargs): The email address associated with this indicator (EmailAddress
            specific summary field).
        associated_artifacts (Artifacts, kwargs): A list of Artifacts associated with this
            Indicator.
        associated_cases (Cases, kwargs): A list of Cases associated with this Indicator.
        associated_groups (Groups, kwargs): A list of groups that this indicator is associated with.
        associated_indicators (Indicators, kwargs): A list of indicators associated with this
            indicator.
        attributes (IndicatorAttributes, kwargs): A list of Attributes corresponding to the
            Indicator.
        confidence (int, kwargs): The indicator threat confidence.
        custom_association_names (array, kwargs): The custom association names assigned to this
            indicator.
        custom_associations (Indicators, kwargs): A list of indicators with custom associations to
            this indicator.
        dns_active (bool, kwargs): Is dns active for the indicator?
        external_date_added (str, kwargs): The date and time that the item was first created
            externally.
        external_date_expires (str, kwargs): The date and time the item expires externally.
        external_last_modified (str, kwargs): The date and time the item was modified externally.
        file_actions (FileActions, kwargs): The type of file action associated with this indicator.
        file_occurrences (FileOccurrences, kwargs): A list of file occurrences associated with this
            indicator.
        first_seen (str, kwargs): The date and time that the item was first seen.
        host_name (str, kwargs): The host name of the indicator (Host specific summary field).
        ip (str, kwargs): The ip address associated with this indicator (Address specific summary
            field).
        last_seen (str, kwargs): The date and time that the item was last seen.
        md5 (str, kwargs): The md5 associated with this indicator (File specific summary field).
        mode (str, kwargs): The operation to perform on the file hashes (delete | merge).
        owner_id (int, kwargs): The id of the Organization, Community, or Source that the item
            belongs to.
        owner_name (str, kwargs): The name of the Organization, Community, or Source that the item
            belongs to.
        private_flag (bool, kwargs): Is this indicator private?
        rating (int, kwargs): The indicator threat rating.
        security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
            Intel item (NOTE: Setting this parameter will replace any existing tag(s) with
            the one(s) specified).
        sha1 (str, kwargs): The sha1 associated with this indicator (File specific summary field).
        sha256 (str, kwargs): The sha256 associated with this indicator (File specific summary
            field).
        size (int, kwargs): The size of the file.
        tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this parameter
            will replace any existing tag(s) with the one(s) specified).
        text (str, kwargs): The url text value of the indicator (Url specific summary field).
        type (str, kwargs): The **type** for the Indicator.
        value1 (str, kwargs): Custom Indicator summary field value1.
        value2 (str, kwargs): Custom Indicator summary field value2.
        value3 (str, kwargs): Custom Indicator summary field value3.
        whois_active (bool, kwargs): Is whois active for the indicator?
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: IndicatorModel = IndicatorModel(**kwargs)
        self._nested_field_name = 'associatedIndicators'
        self._nested_filter = 'has_indicator'
        self.type_ = 'Indicator'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATORS.value

    @property
    def model(self) -> IndicatorModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | IndicatorModel):
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

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}

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
    def associated_groups(self) -> Generator['Group', None, None]:
        """Yield Group from Groups."""
        # first-party
        from tcex.api.tc.v3.groups.group import Groups

        yield from self._iterate_over_sublist(Groups)  # type: ignore

    @property
    def associated_indicators(self) -> Generator[Self, None, None]:
        """Yield Indicator from Indicators."""
        # Ensure the current item is not returned as a association
        for indicator in self._iterate_over_sublist(Indicators):  # type: ignore
            if indicator.model.id == self.model.id:
                continue
            yield indicator  # type: ignore

    @property
    def custom_associations(self) -> Generator[Self, None, None]:
        """Yield Indicator from Indicators."""
        yield from self._iterate_over_sublist(Indicators, custom_associations=True)  # type: ignore

    @property
    def attributes(self) -> Generator['IndicatorAttribute', None, None]:
        """Yield Attribute from Attributes."""
        # first-party
        from tcex.api.tc.v3.indicator_attributes.indicator_attribute import IndicatorAttributes

        yield from self._iterate_over_sublist(IndicatorAttributes)  # type: ignore

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

    def stage_attribute(self, data: dict | ObjectABC | IndicatorAttributeModel):
        """Stage attribute on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = IndicatorAttributeModel(**data)

        if not isinstance(data, IndicatorAttributeModel):
            raise RuntimeError('Invalid type passed in to stage_attribute')
        data._staged = True
        self.model.attributes.data.append(data)  # type: ignore

    def stage_file_action(self, data: dict | ObjectABC | FileActionModel):
        """Stage file_action on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = FileActionModel(**data)

        if not isinstance(data, FileActionModel):
            raise RuntimeError('Invalid type passed in to stage_file_action')
        data._staged = True
        data.indicator._staged = True
        self.model.file_actions.data.append(data)  # type: ignore

    def stage_file_occurrence(self, data: dict | ObjectABC | FileOccurrenceModel):
        """Stage file_occurrence on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = FileOccurrenceModel(**data)

        if not isinstance(data, FileOccurrenceModel):
            raise RuntimeError('Invalid type passed in to stage_file_occurrence')
        data._staged = True
        self.model.file_occurrences.data.append(data)  # type: ignore

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


class Indicators(ObjectCollectionABC):
    """Indicators Collection.

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
        self._model = IndicatorsModel(**kwargs)
        self.type_ = 'indicators'

    def __iter__(self) -> Iterator[Indicator]:
        """Return CM objects."""
        return self.iterate(base_class=Indicator)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATORS.value

    @property
    def filter(self) -> IndicatorFilter:
        """Return the type specific filter object."""
        return IndicatorFilter(self.tql)

    def deleted(
        self,
        deleted_since: datetime | str | None,
        type_: str | None = None,
        owner: str | None = None,
    ):
        """Return deleted indicators.

        This will not use the default params set on the "Indicators"
        object and instead used the params that are passed in.
        """

        if deleted_since is not None:
            deleted_since = str(
                self.util.any_to_datetime(deleted_since).strftime('%Y-%m-%dT%H:%M:%SZ')
            )

        yield from self.iterate(
            base_class=Indicator,
            api_endpoint=f'{self._api_endpoint}/deleted',
            params={'deletedSince': deleted_since, 'owner': owner, 'type': type_},
        )
