"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class GroupModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Group Model',
    validate_assignment=True,
):
    """Group Model"""

    _associated_type: bool = PrivateAttr(default=True)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    ai_provider: str | None = Field(
        default=None,
        description='The provider of the AI generated insights.',
        frozen=True,
        title='aiProvider',
        validate_default=True,
        json_schema_extra={'applies_to': ['Document', 'Report', 'Event']},
    )
    assignments: TaskAssigneesModel | None = Field(
        default=None,
        description=(
            'A list of assignees and escalatees associated with this group (Task specific).'
        ),
        title='assignments',
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
    attributes: GroupAttributesModel | None = Field(
        default=None,
        description='A list of Attributes corresponding to the Group.',
        title='attributes',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    body: str | None = Field(
        default=None,
        description='The email Body.',
        title='body',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email'], 'methods': ['POST', 'PUT']},
    )
    common_group: dict | None = Field(
        default=None,
        description='The common data shared across groups by name and type.',
        frozen=True,
        title='commonGroup',
        validate_default=True,
    )
    created_by: UserModel | None = Field(
        default=None,
        description='The **created by** for the Group.',
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
    document_date_added: datetime | None = Field(
        default=None,
        description='The date and time that the document was first created.',
        frozen=True,
        title='documentDateAdded',
        validate_default=True,
        json_schema_extra={'applies_to': ['Document', 'Report']},
    )
    document_type: str | None = Field(
        default=None,
        description='The document type.',
        frozen=True,
        title='documentType',
        validate_default=True,
        json_schema_extra={'applies_to': ['Document', 'Report']},
    )
    down_vote_count: int | None = Field(
        default=None,
        description='The total number of users who find the intel not helpful.',
        frozen=True,
        title='downVoteCount',
        validate_default=True,
    )
    due_date: datetime | None = Field(
        default=None,
        description='The date and time that the Task is due.',
        title='dueDate',
        validate_default=True,
        json_schema_extra={'applies_to': ['Task'], 'methods': ['POST', 'PUT']},
    )
    email_date: datetime | None = Field(
        default=None,
        description='The date and time that the email was first created.',
        frozen=True,
        title='emailDate',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email']},
    )
    escalated: bool | None = Field(
        default=None,
        description='Flag indicating whether or not the task has been escalated.',
        frozen=True,
        title='escalated',
        validate_default=True,
        json_schema_extra={'applies_to': ['Task']},
    )
    escalation_date: datetime | None = Field(
        default=None,
        description='The escalation date and time.',
        title='escalationDate',
        validate_default=True,
        json_schema_extra={'applies_to': ['Task'], 'methods': ['POST', 'PUT']},
    )
    event_date: datetime | None = Field(
        default=None,
        description='The date and time that the incident or event was first created.',
        title='eventDate',
        validate_default=True,
        json_schema_extra={'applies_to': ['Incident', 'Event'], 'methods': ['POST', 'PUT']},
    )
    event_type: str | None = Field(
        default=None,
        description='The identification of an event type.',
        title='eventType',
        validate_default=True,
        json_schema_extra={'applies_to': ['Event'], 'methods': ['POST', 'PUT']},
    )
    external_date_added: datetime | None = Field(
        default=None,
        description='The date and time that the item was first created externally.',
        title='externalDateAdded',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    external_date_expires: datetime | None = Field(
        default=None,
        description='The date and time the item expires externally.',
        title='externalDateExpires',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    external_last_modified: datetime | None = Field(
        default=None,
        description='The date and time the item was modified externally.',
        title='externalLastModified',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    file_name: str | None = Field(
        default=None,
        description='The document or signature file name.',
        title='fileName',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['Document', 'Report', 'Signature'],
            'conditional_required': ['Document', 'Report', 'Signature'],
            'methods': ['POST', 'PUT'],
        },
    )
    file_size: int | None = Field(
        default=None,
        description='The document file size.',
        frozen=True,
        title='fileSize',
        validate_default=True,
        json_schema_extra={'applies_to': ['Document', 'Report']},
    )
    file_text: str | None = Field(
        default=None,
        description='The signature file text.',
        title='fileText',
        validate_default=True,
        json_schema_extra={'applies_to': ['Signature'], 'methods': ['POST', 'PUT']},
    )
    file_type: str | None = Field(
        default=None,
        description='The signature file type.',
        title='fileType',
        validate_default=True,
        json_schema_extra={'applies_to': ['Signature'], 'methods': ['POST', 'PUT']},
    )
    first_seen: datetime | None = Field(
        default=None,
        description='The date and time that the item was first seen.',
        title='firstSeen',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    from_: str | None = Field(
        default=None,
        alias='from',
        description='The email From field.',
        title='from',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email'], 'methods': ['POST', 'PUT']},
    )
    generated_report: bool | None = Field(
        default=None,
        description='Is the report auto-generated?',
        frozen=True,
        title='generatedReport',
        validate_default=True,
    )
    header: str | None = Field(
        default=None,
        description='The email Header field.',
        title='header',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email'], 'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    insights: dict | None = Field(
        default=None,
        description='An AI generated synopsis of the document.',
        frozen=True,
        title='insights',
        validate_default=True,
        json_schema_extra={'applies_to': ['Document', 'Report', 'Event']},
    )
    last_modified: datetime | None = Field(
        default=None,
        description='The date and time that the Entity was last modified.',
        frozen=True,
        title='lastModified',
        validate_default=True,
    )
    last_seen: datetime | None = Field(
        default=None,
        description='The date and time that the item was last seen.',
        title='lastSeen',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    legacy_link: str | None = Field(
        default=None,
        description='A link to the legacy ThreatConnect details page for this entity.',
        frozen=True,
        title='legacyLink',
        validate_default=True,
    )
    malware: bool | None = Field(
        default=None,
        description='Is the document malware?',
        title='malware',
        validate_default=True,
        json_schema_extra={'applies_to': ['Document'], 'methods': ['POST', 'PUT']},
    )
    name: str | None = Field(
        default=None,
        description='The name of the group.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    overdue: bool | None = Field(
        default=None,
        description='Flag indicating whether or not the task is overdue.',
        frozen=True,
        title='overdue',
        validate_default=True,
        json_schema_extra={'applies_to': ['Task']},
    )
    owner_id: int | None = Field(
        default=None,
        description='The id of the Organization, Community, or Source that the item belongs to.',
        title='ownerId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    owner_name: str | None = Field(
        default=None,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        title='ownerName',
        validate_default=True,
        json_schema_extra={'conditional_read_only': ['Victim'], 'methods': ['POST']},
    )
    password: str | None = Field(
        default=None,
        description='The password associated with the document (Required if Malware is true).',
        title='password',
        validate_default=True,
        json_schema_extra={'applies_to': ['Document'], 'methods': ['POST', 'PUT']},
    )
    publish_date: datetime | None = Field(
        default=None,
        description='The date and time that the report was first created.',
        title='publishDate',
        validate_default=True,
        json_schema_extra={'applies_to': ['Report'], 'methods': ['POST', 'PUT']},
    )
    reminded: bool | None = Field(
        default=None,
        description='Flag indicating whether or not the task reminders have been sent.',
        frozen=True,
        title='reminded',
        validate_default=True,
        json_schema_extra={'applies_to': ['Task']},
    )
    reminder_date: datetime | None = Field(
        default=None,
        description='The reminder date and time.',
        title='reminderDate',
        validate_default=True,
        json_schema_extra={'applies_to': ['Task'], 'methods': ['POST', 'PUT']},
    )
    reviews: dict | None = Field(
        default=None,
        description='A list of reviews corresponding to the Group.',
        title='reviews',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    score: int | None = Field(
        default=None,
        description='The score value for this email.',
        frozen=True,
        title='score',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email']},
    )
    score_breakdown: str | None = Field(
        default=None,
        description='The email score breakdown.',
        frozen=True,
        title='scoreBreakdown',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email']},
    )
    score_includes_body: bool | None = Field(
        default=None,
        description='Is the Body included in the email score?',
        frozen=True,
        title='scoreIncludesBody',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email']},
    )
    security_labels: SecurityLabelsModel | None = Field(
        default=None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        title='securityLabels',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    signature_date_added: datetime | None = Field(
        default=None,
        description='The date and time that the signature was first created.',
        frozen=True,
        title='signatureDateAdded',
        validate_default=True,
        json_schema_extra={'applies_to': ['Signature']},
    )
    status: str | None = Field(
        default=None,
        description=(
            'The status associated with this document, event, task, or incident (read only for '
            'task, document, and report).'
        ),
        title='status',
        validate_default=True,
        json_schema_extra={
            'applies_to': ['Document', 'Report', 'Event', 'Task', 'Incident'],
            'conditional_read_only': ['Document', 'Report', 'Task'],
            'methods': ['POST', 'PUT'],
        },
    )
    subject: str | None = Field(
        default=None,
        description='The email Subject section.',
        title='subject',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email'], 'methods': ['POST', 'PUT']},
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
    to: str | None = Field(
        default=None,
        description='The email To field .',
        frozen=True,
        title='to',
        validate_default=True,
        json_schema_extra={'applies_to': ['Email']},
    )
    type: str | None = Field(
        default=None,
        description='The **type** for the Group.',
        title='type',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    up_vote: bool | None = Field(
        default=None,
        description=(
            'Is the intelligence valid and useful? (0 means downvote, 1 means upvote, and NULL '
            'means no vote).'
        ),
        frozen=True,
        title='upVote',
        validate_default=True,
    )
    up_vote_count: int | None = Field(
        default=None,
        description='The total number of users who find the intel useful.',
        frozen=True,
        title='upVoteCount',
        validate_default=True,
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

    @field_validator('attributes', mode='before')
    @classmethod
    def _validate_group_attributes(cls, v):
        if not v:
            return GroupAttributesModel()  # type: ignore
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

    @field_validator('security_labels', mode='before')
    @classmethod
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()  # type: ignore
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v

    @field_validator('assignments', mode='before')
    @classmethod
    def _validate_task_assignees(cls, v):
        if not v:
            return TaskAssigneesModel()  # type: ignore
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


class GroupDataModel(
    BaseModel,
    title='Group Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Groups Data Model"""

    data: list[GroupModel] | None = Field(
        [],
        description='The data for the Groups.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class GroupsModel(
    BaseModel,
    title='Groups Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Groups Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list[GroupModel] | None = Field(
        [],
        description='The data for the Groups.',
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
from tcex.api.tc.v3.group_attributes.group_attribute_model import GroupAttributesModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.security.task_assignee_model import TaskAssigneesModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetsModel
