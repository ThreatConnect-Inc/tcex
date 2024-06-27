"""TcEx Framework Module"""

# standard library
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorModel
from tcex.api.tc.v3.intel_requirements.intel_requirement_filter import IntelRequirementFilter
from tcex.api.tc.v3.intel_requirements.intel_requirement_model import (
    IntelRequirementModel,
    IntelRequirementsModel,
)
from tcex.api.tc.v3.intel_requirements.keyword_sections.keyword_section_model import (
    KeywordSectionModel,
)
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tags.tag_model import TagModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.cases.case import Case  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.groups.group import Group  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.indicators.indicator import Indicator  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.tags.tag import Tag  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.victim_assets.victim_asset import VictimAsset  # CIRCULAR-IMPORT


class IntelRequirement(ObjectABC):
    """IntelRequirements Object.

    Args:
        associated_artifacts (Artifacts, kwargs): A list of Artifacts associated with this Group.
        associated_cases (Cases, kwargs): A list of Cases associated with this Group.
        associated_groups (Groups, kwargs): A list of groups associated with this group.
        associated_indicators (Indicators, kwargs): A list of indicators associated with this group.
        associated_victim_assets (VictimAssets, kwargs): A list of victim assets associated with
            this group.
        category (IntelReqType, kwargs): The category of the intel requirement.
        description (str, kwargs): The description of the intel requirement.
        keyword_sections (array, kwargs): The section of the intel requirement that contains the
            keywords.
        requirement_text (str, kwargs): The detailed text of the intel requirement.
        reset_results (bool, kwargs): Flag to reset results when updating keywords.
        subtype (IntelReqType, kwargs): The subtype of the intel requirement.
        tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this parameter
            will replace any existing tag(s) with the one(s) specified).
        unique_id (str, kwargs): The unique id of the intel requirement.
        xid (str, kwargs): The xid of the item.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: IntelRequirementModel = IntelRequirementModel(**kwargs)
        self._nested_field_name = 'intelRequirements'
        self._nested_filter = 'has_intel_requirement'
        self.type_ = 'Intel Requirement'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INTEL_REQUIREMENTS.value

    @property
    def model(self) -> IntelRequirementModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | IntelRequirementModel):
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

        return {'type': type_, 'id': self.model.id, 'value': self.model.requirement_text}

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
    def tags(self) -> Generator['Tag', None, None]:
        """Yield Tag from Tags."""
        # first-party
        from tcex.api.tc.v3.tags.tag import Tags

        yield from self._iterate_over_sublist(Tags)  # type: ignore

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

    def replace_keyword_section(self, data: dict | list | ObjectABC | KeywordSectionModel):
        """Replace keyword_section on the object."""
        if not isinstance(data, list):
            data = [data]

        if all(isinstance(item, (KeywordSectionModel, ObjectABC)) for item in data):
            transformed_data = data
        elif all(isinstance(item, dict) for item in data):
            transformed_data = [KeywordSectionModel(**d) for d in data]
        else:
            raise ValueError('Invalid data to replace_keyword_section')

        for item in transformed_data:
            item._staged = True

        self.model.keyword_sections = transformed_data  # type: ignore

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


class IntelRequirements(ObjectCollectionABC):
    """IntelRequirements Collection.

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
        self._model = IntelRequirementsModel(**kwargs)
        self.type_ = 'intel_requirements'

    def __iter__(self) -> Iterator[IntelRequirement]:
        """Return CM objects."""
        return self.iterate(base_class=IntelRequirement)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.INTEL_REQUIREMENTS.value

    @property
    def filter(self) -> IntelRequirementFilter:
        """Return the type specific filter object."""
        return IntelRequirementFilter(self.tql)
