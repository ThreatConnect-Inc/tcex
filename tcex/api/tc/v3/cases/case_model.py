"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class CaseModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Case Model',
    validate_assignment=True,
):
    """Case Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    artifacts: 'ArtifactsModel' = Field(
        None,
        description='A list of Artifacts corresponding to the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='artifacts',
    )
    assignee: 'AssigneeModel' = Field(
        None,
        description='The user or group Assignee object for the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='assignee',
    )
    associated_cases: 'CasesModel' = Field(
        None,
        description='A list of Cases associated with this Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedCases',
    )
    associated_groups: 'GroupsModel' = Field(
        None,
        description='A list of Groups associated with this Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    associated_indicators: 'IndicatorsModel' = Field(
        None,
        description='A list of Indicators associated with this Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedIndicators',
    )
    attributes: 'CaseAttributesModel' = Field(
        None,
        description='A list of Attributes corresponding to the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='attributes',
    )
    case_close_time: datetime | None = Field(
        None,
        description='The date and time that the Case was closed.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='caseCloseTime',
    )
    case_close_user: 'UserModel' = Field(
        None,
        allow_mutation=False,
        description='The user that closed the Case.',
        read_only=True,
        title='caseCloseUser',
    )
    case_detection_time: datetime | None = Field(
        None,
        description='The date and time that ends the user initiated Case duration.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='caseDetectionTime',
    )
    case_detection_user: 'UserModel' = Field(
        None,
        allow_mutation=False,
        description='The user that stopped the clock on Case duration.',
        read_only=True,
        title='caseDetectionUser',
    )
    case_occurrence_time: datetime | None = Field(
        None,
        description='The date and time that starts the user initiated Case duration.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='caseOccurrenceTime',
    )
    case_occurrence_user: 'UserModel' = Field(
        None,
        allow_mutation=False,
        description='The user that started the clock on Case duration.',
        read_only=True,
        title='caseOccurrenceUser',
    )
    case_open_time: datetime | None = Field(
        None,
        description='The date and time that the Case was first opened.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='caseOpenTime',
    )
    case_open_user: 'UserModel' = Field(
        None,
        allow_mutation=False,
        description='The user that opened the Case.',
        read_only=True,
        title='caseOpenUser',
    )
    created_by: 'UserModel' = Field(
        None,
        allow_mutation=False,
        description='The **created by** for the Case.',
        read_only=True,
        title='createdBy',
    )
    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Case was first created.',
        read_only=True,
        title='dateAdded',
    )
    description: str | None = Field(
        None,
        description='The description of the Case.',
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
    last_updated: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Case was last updated.',
        read_only=True,
        title='lastUpdated',
    )
    name: str | None = Field(
        None,
        description='The name of the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    notes: 'NotesModel' = Field(
        None,
        description='A list of Notes corresponding to the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='notes',
    )
    owner: str | None = Field(
        None,
        allow_mutation=False,
        description='The name of the Owner of the Case.',
        read_only=True,
        title='owner',
    )
    owner_id: int | None = Field(
        None,
        allow_mutation=False,
        description='The id of the Owner of the Case.',
        read_only=True,
        title='ownerId',
    )
    related: 'CasesModel' = Field(
        None,
        allow_mutation=False,
        description='The **related** for the Case.',
        read_only=True,
        title='related',
    )
    resolution: str | None = Field(
        None,
        description='The Case resolution.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='resolution',
    )
    severity: str | None = Field(
        None,
        description='The Case severity.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='severity',
    )
    status: str | None = Field(
        None,
        description='The Case status.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='status',
    )
    tags: 'TagsModel' = Field(
        None,
        description=(
            'A list of Tags corresponding to the Case (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='tags',
    )
    tasks: 'TasksModel' = Field(
        None,
        description='A list of Tasks corresponding to the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='tasks',
    )
    user_access: 'UsersModel' = Field(
        None,
        description=(
            'A list of Users that, when defined, are the only ones allowed to view or edit the '
            'Case.'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='userAccess',
    )
    workflow_events: 'WorkflowEventsModel' = Field(
        None,
        description='A list of workflowEvents (timeline) corresponding to the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='workflowEvents',
    )
    workflow_template: 'WorkflowTemplateModel' = Field(
        None,
        description='The Template that the Case is populated by.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='workflowTemplate',
    )
    xid: str | None = Field(
        None,
        description='The **xid** for the Case.',
        methods=['POST'],
        read_only=False,
        title='xid',
    )

    @validator('artifacts', always=True, pre=True)
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()  # type: ignore
        return v

    @validator('assignee', always=True, pre=True)
    def _validate_assignee(cls, v):
        if not v:
            return AssigneeModel()  # type: ignore
        return v

    @validator('attributes', always=True, pre=True)
    def _validate_case_attributes(cls, v):
        if not v:
            return CaseAttributesModel()  # type: ignore
        return v

    @validator('associated_cases', 'related', always=True, pre=True)
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

    @validator('notes', always=True, pre=True)
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()  # type: ignore
        return v

    @validator('tags', always=True, pre=True)
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v

    @validator('tasks', always=True, pre=True)
    def _validate_tasks(cls, v):
        if not v:
            return TasksModel()  # type: ignore
        return v

    @validator(
        'case_close_user',
        'case_detection_user',
        'case_occurrence_user',
        'case_open_user',
        'created_by',
        always=True,
        pre=True,
    )
    def _validate_user(cls, v):
        if not v:
            return UserModel()  # type: ignore
        return v

    @validator('user_access', always=True, pre=True)
    def _validate_users(cls, v):
        if not v:
            return UsersModel()  # type: ignore
        return v

    @validator('workflow_events', always=True, pre=True)
    def _validate_workflow_events(cls, v):
        if not v:
            return WorkflowEventsModel()  # type: ignore
        return v

    @validator('workflow_template', always=True, pre=True)
    def _validate_workflow_template(cls, v):
        if not v:
            return WorkflowTemplateModel()  # type: ignore
        return v


class CaseDataModel(
    BaseModel,
    title='Case Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Cases Data Model"""

    data: list[CaseModel] | None = Field(
        [],
        description='The data for the Cases.',
        methods=['POST', 'PUT'],
        title='data',
    )


class CasesModel(
    BaseModel,
    title='Cases Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Cases Model"""

    _mode_support = PrivateAttr(True)

    data: list[CaseModel] | None = Field(
        [],
        description='The data for the Cases.',
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
from tcex.api.tc.v3.case_attributes.case_attribute_model import CaseAttributesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.notes.note_model import NotesModel
from tcex.api.tc.v3.security.assignee_model import AssigneeModel
from tcex.api.tc.v3.security.users.user_model import UserModel, UsersModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
from tcex.api.tc.v3.tasks.task_model import TasksModel
from tcex.api.tc.v3.workflow_events.workflow_event_model import WorkflowEventsModel
from tcex.api.tc.v3.workflow_templates.workflow_template_model import WorkflowTemplateModel

# add forward references
CaseDataModel.update_forward_refs()
CaseModel.update_forward_refs()
CasesModel.update_forward_refs()
