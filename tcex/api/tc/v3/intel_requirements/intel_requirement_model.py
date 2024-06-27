"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class IntelRequirementModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='IntelRequirement Model',
    validate_assignment=True,
):
    """Intel_Requirement Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    associated_artifacts: 'ArtifactsModel' = Field(
        None,
        description='A list of Artifacts associated with this Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedArtifacts',
    )
    associated_cases: 'CasesModel' = Field(
        None,
        description='A list of Cases associated with this Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedCases',
    )
    associated_groups: 'GroupsModel' = Field(
        None,
        description='A list of groups associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    associated_indicators: 'IndicatorsModel' = Field(
        None,
        description='A list of indicators associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedIndicators',
    )
    associated_victim_assets: 'VictimAssetsModel' = Field(
        None,
        description='A list of victim assets associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedVictimAssets',
    )
    category: 'IntelReqTypeModel' = Field(
        None,
        description='The category of the intel requirement.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='category',
    )
    created_by: 'UserModel' = Field(
        None,
        allow_mutation=False,
        description='The user who created the intel requirement.',
        read_only=True,
        title='createdBy',
    )
    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    description: str | None = Field(
        None,
        description='The description of the intel requirement.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='description',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    keyword_sections: list['KeywordSectionModel'] = Field(
        None,
        description='The section of the intel requirement that contains the keywords.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='keywordSections',
    )
    last_modified: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Entity was last modified.',
        read_only=True,
        title='lastModified',
    )
    last_retrieved_date: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The last date the results were retrieved for the intel requirement.',
        read_only=True,
        title='lastRetrievedDate',
    )
    requirement_text: str | None = Field(
        None,
        description='The detailed text of the intel requirement.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='requirementText',
    )
    reset_results: bool = Field(
        None,
        description='Flag to reset results when updating keywords.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='resetResults',
    )
    results_link: str | None = Field(
        None,
        allow_mutation=False,
        description='A link to the results for the intel requirement.',
        read_only=True,
        title='resultsLink',
    )
    subtype: 'IntelReqTypeModel' = Field(
        None,
        description='The subtype of the intel requirement.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='subtype',
    )
    tags: 'TagsModel' = Field(
        None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='tags',
    )
    unique_id: str | None = Field(
        None,
        description='The unique id of the intel requirement.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='uniqueId',
    )
    web_link: str | None = Field(
        None,
        allow_mutation=False,
        description='A link to the ThreatConnect details page for this entity.',
        read_only=True,
        title='webLink',
    )
    xid: str | None = Field(
        None,
        description='The xid of the item.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='xid',
    )

    @validator('associated_artifacts', always=True, pre=True)
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()  # type: ignore
        return v

    @validator('associated_cases', always=True, pre=True)
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()  # type: ignore
        return v

    @validator('associated_groups', always=True, pre=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()  # type: ignore
        return v

    @validator('associated_indicators', always=True, pre=True)
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()  # type: ignore
        return v

    @validator('category', 'subtype', always=True, pre=True)
    def _validate_intel_req_type(cls, v):
        if not v:
            return IntelReqTypeModel()  # type: ignore
        return v

    @validator('keyword_sections', always=True, pre=True)
    def _validate_keyword_section(cls, v):
        if not v:
            return list['KeywordSectionModel']()  # type: ignore
        return v

    @validator('tags', always=True, pre=True)
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v

    @validator('created_by', always=True, pre=True)
    def _validate_user(cls, v):
        if not v:
            return UserModel()  # type: ignore
        return v

    @validator('associated_victim_assets', always=True, pre=True)
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
        methods=['POST', 'PUT'],
        title='data',
    )


class IntelRequirementsModel(
    BaseModel,
    title='IntelRequirements Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Intel_Requirements Model"""

    _mode_support = PrivateAttr(False)

    data: list[IntelRequirementModel] | None = Field(
        [],
        description='The data for the IntelRequirements.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


# first-party
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

# add forward references
IntelRequirementDataModel.update_forward_refs()
IntelRequirementModel.update_forward_refs()
IntelRequirementsModel.update_forward_refs()
