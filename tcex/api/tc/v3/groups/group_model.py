"""Group / Groups Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class GroupsModel(
    BaseModel,
    title='Groups Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Groups Model"""

    _mode_support = PrivateAttr(True)

    data: Optional[List['GroupModel']] = Field(
        [],
        description='The data for the Groups.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class GroupDataModel(
    BaseModel,
    title='Group Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Groups Data Model"""

    data: Optional[List['GroupModel']] = Field(
        [],
        description='The data for the Groups.',
        methods=['POST', 'PUT'],
        title='data',
    )


class GroupModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Group Model',
    validate_assignment=True,
):
    """Group Model"""

    _associated_type = PrivateAttr(True)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    assignments: Optional['TaskAssigneesModel'] = Field(
        None,
        description=(
            'A list of assignees and escalatees associated with this group (Task specific).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='assignments',
    )
    associated_artifacts: Optional['ArtifactsModel'] = Field(
        None,
        description='A list of Artifacts associated with this Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedArtifacts',
    )
    associated_cases: Optional['CasesModel'] = Field(
        None,
        description='A list of Cases associated with this Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedCases',
    )
    associated_groups: Optional['GroupsModel'] = Field(
        None,
        description='A list of groups associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    associated_indicators: Optional['IndicatorsModel'] = Field(
        None,
        description='A list of indicators associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedIndicators',
    )
    associated_victim_assets: Optional['VictimAssetsModel'] = Field(
        None,
        description='A list of victim assets associated with this group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedVictimAssets',
    )
    attributes: Optional['GroupAttributesModel'] = Field(
        None,
        description='A list of Attributes corresponding to the Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='attributes',
    )
    body: Optional[str] = Field(
        None,
        applies_to=['Email'],
        description='The email Body.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='body',
    )
    created_by: Optional['UserModel'] = Field(
        None,
        allow_mutation=False,
        description='The **created by** for the Group.',
        read_only=True,
        title='createdBy',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    document_date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        applies_to=['Document', 'Report'],
        description='The date and time that the document was first created.',
        read_only=True,
        title='documentDateAdded',
    )
    document_type: Optional[str] = Field(
        None,
        allow_mutation=False,
        applies_to=['Document', 'Report'],
        description='The document type.',
        read_only=True,
        title='documentType',
    )
    down_vote_count: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The total number of users who find the intel not helpful.',
        read_only=True,
        title='downVoteCount',
    )
    due_date: Optional[datetime] = Field(
        None,
        applies_to=['Task'],
        description='The date and time that the Task is due.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='dueDate',
    )
    email_date: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        applies_to=['Email'],
        description='The date and time that the email was first created.',
        read_only=True,
        title='emailDate',
    )
    escalated: bool = Field(
        None,
        allow_mutation=False,
        applies_to=['Task'],
        description='Flag indicating whether or not the task has been escalated.',
        read_only=True,
        title='escalated',
    )
    escalation_date: Optional[datetime] = Field(
        None,
        applies_to=['Task'],
        description='The escalation date and time.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='escalationDate',
    )
    event_date: Optional[datetime] = Field(
        None,
        applies_to=['Incident', 'Event'],
        description='The date and time that the incident or event was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='eventDate',
    )
    external_date_added: Optional[datetime] = Field(
        None,
        description='The date and time that the item was first created externally.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='externalDateAdded',
    )
    external_date_expires: Optional[datetime] = Field(
        None,
        description='The date and time the item expires externally.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='externalDateExpires',
    )
    external_last_modified: Optional[datetime] = Field(
        None,
        description='The date and time the item was modified externally.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='externalLastModified',
    )
    file_name: Optional[str] = Field(
        None,
        applies_to=['Document', 'Report', 'Signature'],
        conditional_required=['Document', 'Report', 'Signature'],
        description='The document or signature file name.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileName',
    )
    file_size: Optional[int] = Field(
        None,
        allow_mutation=False,
        applies_to=['Document', 'Report'],
        description='The document file size.',
        read_only=True,
        title='fileSize',
    )
    file_text: Optional[str] = Field(
        None,
        applies_to=['Signature'],
        description='The signature file text.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileText',
    )
    file_type: Optional[str] = Field(
        None,
        applies_to=['Signature'],
        description='The signature file type.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='fileType',
    )
    first_seen: Optional[datetime] = Field(
        None,
        description='The date and time that the item was first seen.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='firstSeen',
    )
    from_: Optional[str] = Field(
        None,
        alias='from',
        applies_to=['Email'],
        description='The email From field.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='from',
    )
    generated_report: bool = Field(
        None,
        allow_mutation=False,
        description='Is the report auto-generated?',
        read_only=True,
        title='generatedReport',
    )
    header: Optional[str] = Field(
        None,
        applies_to=['Email'],
        description='The email Header field.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='header',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    last_modified: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Entity was last modified.',
        read_only=True,
        title='lastModified',
    )
    last_seen: Optional[datetime] = Field(
        None,
        description='The date and time that the item was last seen.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='lastSeen',
    )
    legacy_link: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='A link to the legacy ThreatConnect details page for this entity.',
        read_only=True,
        title='legacyLink',
    )
    malware: bool = Field(
        None,
        applies_to=['Document'],
        description='Is the document malware?',
        methods=['POST', 'PUT'],
        read_only=False,
        title='malware',
    )
    name: Optional[str] = Field(
        None,
        description='The name of the group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    overdue: bool = Field(
        None,
        allow_mutation=False,
        applies_to=['Task'],
        description='Flag indicating whether or not the task is overdue.',
        read_only=True,
        title='overdue',
    )
    owner_id: Optional[int] = Field(
        None,
        description='The id of the Organization, Community, or Source that the item belongs to.',
        methods=['POST'],
        read_only=False,
        title='ownerId',
    )
    owner_name: Optional[str] = Field(
        None,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        methods=['POST'],
        read_only=False,
        title='ownerName',
    )
    password: Optional[str] = Field(
        None,
        applies_to=['Document'],
        description='The password associated with the document (Required if Malware is true).',
        methods=['POST', 'PUT'],
        read_only=False,
        title='password',
    )
    publish_date: Optional[datetime] = Field(
        None,
        applies_to=['Report'],
        description='The date and time that the report was first created.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='publishDate',
    )
    reminded: bool = Field(
        None,
        allow_mutation=False,
        applies_to=['Task'],
        description='Flag indicating whether or not the task reminders have been sent.',
        read_only=True,
        title='reminded',
    )
    reminder_date: Optional[datetime] = Field(
        None,
        applies_to=['Task'],
        description='The reminder date and time.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='reminderDate',
    )
    score: Optional[int] = Field(
        None,
        allow_mutation=False,
        applies_to=['Email'],
        description='The score value for this email.',
        read_only=True,
        title='score',
    )
    score_breakdown: Optional[str] = Field(
        None,
        allow_mutation=False,
        applies_to=['Email'],
        description='The email score breakdown.',
        read_only=True,
        title='scoreBreakdown',
    )
    score_includes_body: bool = Field(
        None,
        allow_mutation=False,
        applies_to=['Email'],
        description='Is the Body included in the email score?',
        read_only=True,
        title='scoreIncludesBody',
    )
    security_labels: Optional['SecurityLabelsModel'] = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityLabels',
    )
    signature_date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        applies_to=['Signature'],
        description='The date and time that the signature was first created.',
        read_only=True,
        title='signatureDateAdded',
    )
    status: Optional[str] = Field(
        None,
        applies_to=['Document', 'Report', 'Event', 'Task', 'Incident'],
        description=(
            'The status associated with this document, event, task, or incident (read only for '
            'task, document, and report).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='status',
    )
    subject: Optional[str] = Field(
        None,
        applies_to=['Email'],
        description='The email Subject section.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='subject',
    )
    tags: Optional['TagsModel'] = Field(
        None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='tags',
    )
    to: Optional[str] = Field(
        None,
        allow_mutation=False,
        applies_to=['Email'],
        description='The email To field .',
        read_only=True,
        title='to',
    )
    type: Optional[str] = Field(
        None,
        description='The **type** for the Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='type',
    )
    up_vote: bool = Field(
        None,
        description=(
            'Is the intelligence valid and useful? (0 means downvote, 1 means upvote, and NULL '
            'means no vote).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='upVote',
    )
    up_vote_count: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The total number of users who find the intel useful.',
        read_only=True,
        title='upVoteCount',
    )
    web_link: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='A link to the ThreatConnect details page for this entity.',
        read_only=True,
        title='webLink',
    )
    xid: Optional[str] = Field(
        None,
        description='The xid of the item.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='xid',
    )

    @validator('associated_artifacts', always=True)
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()
        return v

    @validator('associated_cases', always=True)
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()
        return v

    @validator('attributes', always=True)
    def _validate_group_attributes(cls, v):
        if not v:
            return GroupAttributesModel()
        return v

    @validator('associated_groups', always=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()
        return v

    @validator('associated_indicators', always=True)
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()
        return v

    @validator('security_labels', always=True)
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()
        return v

    @validator('tags', always=True)
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()
        return v

    @validator('assignments', always=True)
    def _validate_task_assignees(cls, v):
        if not v:
            return TaskAssigneesModel()
        return v

    @validator('created_by', always=True)
    def _validate_user(cls, v):
        if not v:
            return UserModel()
        return v

    @validator('associated_victim_assets', always=True)
    def _validate_victim_assets(cls, v):
        if not v:
            return VictimAssetsModel()
        return v


# first-party
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactsModel
from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.group_attributes.group_attribute_model import GroupAttributesModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.security.task_assignee_model import TaskAssigneesModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetsModel

# add forward references
GroupDataModel.update_forward_refs()
GroupModel.update_forward_refs()
GroupsModel.update_forward_refs()
