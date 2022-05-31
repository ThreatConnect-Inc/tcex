"""Indicator / Indicators Object"""
# standard library
import json
from datetime import datetime
from typing import TYPE_CHECKING, Iterator, Optional, Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.cases.case_model import CaseModel
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
    from tcex.api.tc.v3.artifacts.artifact import Artifact
    from tcex.api.tc.v3.cases.case import Case
    from tcex.api.tc.v3.groups.group import Group
    from tcex.api.tc.v3.indicator_attributes.indicator_attribute import IndicatorAttribute
    from tcex.api.tc.v3.security_labels.security_label import SecurityLabel
    from tcex.api.tc.v3.tags.tag import Tag


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
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = IndicatorsModel(**kwargs)
        self.type_ = 'indicators'

    def __iter__(self) -> 'Indicator':
        """Iterate over CM objects."""
        return self.iterate(base_class=Indicator)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATORS.value

    @property
    def filter(self) -> 'IndicatorFilter':
        """Return the type specific filter object."""
        return IndicatorFilter(self.tql)

    def deleted(
        self,
        deleted_since: Optional[Union[datetime, str]],
        type_: Optional[str] = None,
        owner: Optional[str] = None,
    ):
        """Return deleted indicators.

        This will not use the default params set on the "Indicators"
        object and instead used the params that are passed in.
        """

        if deleted_since is not None:
            deleted_since = str(
                self.utils.any_to_datetime(deleted_since).strftime('%Y-%m-%dT%H:%M:%SZ')
            )

        yield from self.iterate(
            base_class=Indicator,
            api_endpoint=f'{self._api_endpoint}/deleted',
            params={'deletedSince': deleted_since, 'owner': owner, 'type': type_},
        )


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
        dns_active (bool, kwargs): Is dns active for the indicator?
        host_name (str, kwargs): The host name of the indicator (Host specific summary field).
        ip (str, kwargs): The ip address associated with this indicator (Address specific summary
            field).
        md5 (str, kwargs): The md5 associated with this indicator (File specific summary field).
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
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = IndicatorModel(**kwargs)
        self._nested_field_name = 'associatedIndicators'
        self._nested_filter = 'has_indicator'
        self.type_ = 'Indicator'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INDICATORS.value

    @property
    def model(self) -> 'IndicatorModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['IndicatorModel', dict]):
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
        # first-party
        from tcex.api.tc.v3.groups.group import Groups

        yield from self._iterate_over_sublist(Groups)

    @property
    def associated_indicators(self) -> Iterator['Indicator']:
        """Yield Indicator from Indicators."""
        # Ensure the current item is not returned as a association
        for indicator in self._iterate_over_sublist(Indicators):
            if indicator.model.id == self.model.id:
                continue
            yield indicator

    @property
    def attributes(self) -> Iterator['IndicatorAttribute']:
        """Yield Attribute from Attributes."""
        # first-party
        from tcex.api.tc.v3.indicator_attributes.indicator_attribute import IndicatorAttributes

        yield from self._iterate_over_sublist(IndicatorAttributes)

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

    def stage_attribute(self, data: Union[dict, 'ObjectABC', 'IndicatorAttributeModel']):
        """Stage attribute on the object."""
        if isinstance(data, ObjectABC):
            data = data.model
        elif isinstance(data, dict):
            data = IndicatorAttributeModel(**data)

        if not isinstance(data, IndicatorAttributeModel):
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
