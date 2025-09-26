"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class CaseModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Case Model',
    validate_assignment=True,
):
    """Case Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=True)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    artifacts: ArtifactsModel | None = Field(
        default=None,
        description='A list of Artifacts corresponding to the Case.',
        title='artifacts',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    assignee: AssigneeModel | None = Field(
        default=None,
        description='The user or group Assignee object for the Case.',
        title='assignee',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_cases: CasesModel | None = Field(
        default=None,
        description='A list of Cases associated with this Case.',
        title='associatedCases',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_groups: GroupsModel | None = Field(
        default=None,
        description='A list of Groups associated with this Case.',
        title='associatedGroups',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    associated_indicators: IndicatorsModel | None = Field(
        default=None,
        description='A list of Indicators associated with this Case.',
        title='associatedIndicators',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    attributes: CaseAttributesModel | None = Field(
        default=None,
        description='A list of Attributes corresponding to the Case.',
        title='attributes',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    case_close_time: datetime | None = Field(
        default=None,
        description='The date and time that the Case was closed.',
        title='caseCloseTime',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    case_close_user: UserModel | None = Field(
        default=None,
        description='The user that closed the Case.',
        frozen=True,
        title='caseCloseUser',
        validate_default=True,
    )
    case_detection_time: datetime | None = Field(
        default=None,
        description='The date and time that ends the user initiated Case duration.',
        title='caseDetectionTime',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    case_detection_user: UserModel | None = Field(
        default=None,
        description='The user that stopped the clock on Case duration.',
        frozen=True,
        title='caseDetectionUser',
        validate_default=True,
    )
    case_occurrence_time: datetime | None = Field(
        default=None,
        description='The date and time that starts the user initiated Case duration.',
        title='caseOccurrenceTime',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    case_occurrence_user: UserModel | None = Field(
        default=None,
        description='The user that started the clock on Case duration.',
        frozen=True,
        title='caseOccurrenceUser',
        validate_default=True,
    )
    case_open_time: datetime | None = Field(
        default=None,
        description='The date and time that the Case was first opened.',
        title='caseOpenTime',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    case_open_user: UserModel | None = Field(
        default=None,
        description='The user that opened the Case.',
        frozen=True,
        title='caseOpenUser',
        validate_default=True,
    )
    created_by: UserModel | None = Field(
        default=None,
        description='The **created by** for the Case.',
        frozen=True,
        title='createdBy',
        validate_default=True,
    )
    date_added: datetime | None = Field(
        default=None,
        description='The date and time that the Case was first created.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='The description of the Case.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    detection_due: datetime | None = Field(
        default=None,
        description='The date and time that the Case detection is due.',
        frozen=True,
        title='detectionDue',
        validate_default=True,
    )
    detection_overdue: bool | None = Field(
        default=None,
        description=(
            'Flag indicating whether or not the case detection is overdue, based on the '
            'organization SLA settings.'
        ),
        frozen=True,
        title='detectionOverdue',
        validate_default=True,
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    last_updated: datetime | None = Field(
        default=None,
        description='The date and time that the Case was last updated.',
        frozen=True,
        title='lastUpdated',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The name of the Case.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    notes: NotesModel | None = Field(
        default=None,
        description='A list of Notes corresponding to the Case.',
        title='notes',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    owner: str | None = Field(
        default=None,
        description='The name of the Owner of the Case.',
        frozen=True,
        title='owner',
        validate_default=True,
    )
    owner_id: int | None = Field(
        default=None,
        description='The id of the Owner of the Case.',
        frozen=True,
        title='ownerId',
        validate_default=True,
    )
    related: CasesModel | None = Field(
        default=None,
        description='The **related** for the Case.',
        frozen=True,
        title='related',
        validate_default=True,
    )
    resolution: str | None = Field(
        default=None,
        description='The Case resolution.',
        title='resolution',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    response_due: datetime | None = Field(
        default=None,
        description='The date and time that the Case response is due.',
        frozen=True,
        title='responseDue',
        validate_default=True,
    )
    response_overdue: bool | None = Field(
        default=None,
        description=(
            'Flag indicating whether or not the case response is overdue, based on the organization'
            ' SLA settings.'
        ),
        frozen=True,
        title='responseOverdue',
        validate_default=True,
    )
    severity: str | None = Field(
        default=None,
        description='The Case severity.',
        title='severity',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    status: str | None = Field(
        default=None,
        description='The Case status.',
        title='status',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    tags: TagsModel | None = Field(
        default=None,
        description=(
            'A list of Tags corresponding to the Case (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        title='tags',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    tasks: TasksModel | None = Field(
        default=None,
        description='A list of Tasks corresponding to the Case.',
        title='tasks',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    time_to_detect: int | None = Field(
        default=None,
        description='The resultant time (in seconds) from the case detection time calculation.',
        frozen=True,
        title='timeToDetect',
        validate_default=True,
    )
    time_to_respond: int | None = Field(
        default=None,
        description='The resultant time (in seconds) from the case response time calculation.',
        frozen=True,
        title='timeToRespond',
        validate_default=True,
    )
    user_access: UsersModel | None = Field(
        default=None,
        description=(
            'A list of Users that, when defined, are the only ones allowed to view or edit the '
            'Case.'
        ),
        title='userAccess',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    workflow_events: WorkflowEventsModel | None = Field(
        default=None,
        description='A list of workflowEvents (timeline) corresponding to the Case.',
        title='workflowEvents',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    workflow_template: WorkflowTemplateModel | None = Field(
        default=None,
        description='The Template that the Case is populated by.',
        title='workflowTemplate',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    xid: str | None = Field(
        default=None,
        description='The **xid** for the Case.',
        title='xid',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )

    @field_validator('artifacts', mode='before')
    @classmethod
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()  # type: ignore
        return v

    @field_validator('assignee', mode='before')
    @classmethod
    def _validate_assignee(cls, v):
        if not v:
            return AssigneeModel()  # type: ignore
        return v

    @field_validator('attributes', mode='before')
    @classmethod
    def _validate_case_attributes(cls, v):
        if not v:
            return CaseAttributesModel()  # type: ignore
        return v

    @field_validator('associated_cases', 'related', mode='before')
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

    @field_validator('notes', mode='before')
    @classmethod
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()  # type: ignore
        return v

    @field_validator('tags', mode='before')
    @classmethod
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()  # type: ignore
        return v

    @field_validator('tasks', mode='before')
    @classmethod
    def _validate_tasks(cls, v):
        if not v:
            return TasksModel()  # type: ignore
        return v

    @field_validator(
        'case_close_user',
        'case_detection_user',
        'case_occurrence_user',
        'case_open_user',
        'created_by',
        mode='before',
    )
    @classmethod
    def _validate_user(cls, v):
        if not v:
            return UserModel()  # type: ignore
        return v

    @field_validator('user_access', mode='before')
    @classmethod
    def _validate_users(cls, v):
        if not v:
            return UsersModel()  # type: ignore
        return v

    @field_validator('workflow_events', mode='before')
    @classmethod
    def _validate_workflow_events(cls, v):
        if not v:
            return WorkflowEventsModel()  # type: ignore
        return v

    @field_validator('workflow_template', mode='before')
    @classmethod
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
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class CasesModel(
    BaseModel,
    title='Cases Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Cases Model"""

    _mode_support: bool = PrivateAttr(default=True)

    data: list[CaseModel] | None = Field(
        [],
        description='The data for the Cases.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


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
