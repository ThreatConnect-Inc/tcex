"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class IntelRequirementModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='IntelRequirement Model',
    validate_assignment=True,
):
    """Intel_Requirement Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    active: bool | None = Field(
        default=None,
        description='If Intel Requirement is active.',
        title='active',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_artifacts: ArtifactsModel | None = Field(
        default=None,
        description='A list of Artifacts associated with this Group.',
        title='associatedArtifacts',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_cases: CasesModel | None = Field(
        default=None,
        description='A list of Cases associated with this Group.',
        title='associatedCases',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_groups: GroupsModel | None = Field(
        default=None,
        description='A list of groups associated with this group.',
        title='associatedGroups',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_indicators: IndicatorsModel | None = Field(
        default=None,
        description='A list of indicators associated with this group.',
        title='associatedIndicators',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_victim_assets: VictimAssetsModel | None = Field(
        default=None,
        description='A list of victim assets associated with this group.',
        title='associatedVictimAssets',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    category: IntelReqTypeModel | None = Field(
        default=None,
        description='The category of the intel requirement.',
        title='category',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    created_by: UserModel | None = Field(
        default=None,
        description='The user who created the intel requirement.',
        frozen=True,
        title='createdBy',
        validate_default=True,
    )
    date_added: datetime | None = Field(
        default=None,
        description='The date and time that the item was first created.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='The description of the intel requirement.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    earliest_timestamp: datetime | None = Field(
        default=None,
        description='How far in the past the system should look for matches.',
        title='earliestTimestamp',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    keyword_sections: list[KeywordSectionModel | None] | None = Field(
        default=None,
        description='The section of the intel requirement that contains the keywords.',
        title='keywordSections',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    last_modified: datetime | None = Field(
        default=None,
        description='The date and time that the Entity was last modified.',
        frozen=True,
        title='lastModified',
        validate_default=True,
    )
    last_retrieved_date: datetime | None = Field(
        default=None,
        description='The last date the results were retrieved for the intel requirement.',
        frozen=True,
        title='lastRetrievedDate',
        validate_default=True,
    )
    latest_timestamp: datetime | None = Field(
        default=None,
        description='The cutoff point for future data to be considered.',
        title='latestTimestamp',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    requirement_text: str | None = Field(
        default=None,
        description='The detailed text of the intel requirement.',
        title='requirementText',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    reset_results: bool | None = Field(
        default=None,
        description='Flag to reset results when updating keywords.',
        title='resetResults',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    results_link: str | None = Field(
        default=None,
        description='A link to the results for the intel requirement.',
        frozen=True,
        title='resultsLink',
        validate_default=True,
    )
    subtype: IntelReqTypeModel | None = Field(
        default=None,
        description='The subtype of the intel requirement.',
        title='subtype',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    tags: TagsModel | None = Field(
        default=None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        title='tags',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    unique_id: str | None = Field(
        default=None,
        description='The unique id of the intel requirement.',
        title='uniqueId',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    web_link: str | None = Field(
        default=None,
        description='A link to the ThreatConnect details page for this entity.',
        frozen=True,
        title='webLink',
        validate_default=True,
    )
    xid: str | None = Field(
        default=None,
        description='The xid of the item.',
        title='xid',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )

    @field_validator('associated_artifacts', mode='before')
    @classmethod
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()  # type: ignore
        return v

    @field_validator('associated_cases', mode='before')
    @classmethod
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()  # type: ignore
        return v

    @field_validator('associated_groups', mode='before')
    @classmethod
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @field_validator('associated_indicators', mode='before')
    @classmethod
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()  # type: ignore
        return v

    @field_validator('category', 'subtype', mode='before')
    @classmethod
    def _validate_intel_req_type(cls, v):
        if not v:
            return IntelReqTypeModel()  # type: ignore
        return v

    @field_validator('keyword_sections', mode='before')
    @classmethod
    def _validate_keyword_section(cls, v):
        if not v:
            return list['KeywordSectionModel | None']()  # type: ignore
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v

    @field_validator('created_by', mode='before')
    @classmethod
    def _validate_user(cls, v):
        if not v:
            return UserModel()  # type: ignore
        return v

    @field_validator('associated_victim_assets', mode='before')
    @classmethod
    def _validate_victim_assets(cls, v):
        if not v:
            return VictimAssetsModel()  # type: ignore
        return v


class IntelRequirementDataModel(
    BaseModel,
    title='IntelRequirement Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Intel_Requirements Data Model"""

    data: list[IntelRequirementModel] | None = Field(
        [],
        description='The data for the IntelRequirements.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class IntelRequirementsModel(
    BaseModel,
    title='IntelRequirements Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Intel_Requirements Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[IntelRequirementModel] | None = Field(
        [],
        description='The data for the IntelRequirements.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.artifacts.artifact_model import ArtifactsModel
from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.intel_requirements.intel_req_type_model import IntelReqTypeModel
from tcex.api.tc.v3.intel_requirements.keyword_sections.keyword_section_model import (
    KeywordSectionModel,
)
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetsModel

# rebuild model
IntelRequirementDataModel.model_rebuild()
IntelRequirementModel.model_rebuild()
IntelRequirementsModel.model_rebuild()
