"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class TaskModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Task Model',
    validate_assignment=True,
):
    """Task Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=True)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    artifacts: ArtifactsModel | None = Field(
        default=None,
        description='A list of Artifacts corresponding to the Task.',
        title='artifacts',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    assignee: AssigneeModel | None = Field(
        default=None,
        description='The user or group Assignee object for the Task.',
        title='assignee',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    case_id: int | None = Field(
        default=None,
        description='The **case id** for the Task.',
        title='caseId',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseXid'},
    )
    case_xid: str | None = Field(
        default=None,
        description='The **case xid** for the Task.',
        title='caseXid',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseId'},
    )
    completed_by: str | None = Field(
        default=None,
        description='The **completed by** for the Task.',
        frozen=True,
        title='completedBy',
        validate_default=True,
    )
    completed_date: datetime | None = Field(
        default=None,
        description='The completion date of the Task.',
        title='completedDate',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    config_playbook: str | None = Field(
        default=None,
        description='The **config playbook** for the Task.',
        frozen=True,
        title='configPlaybook',
        validate_default=True,
    )
    config_task: dict | list[dict] | None = Field(
        default=None,
        description='The **config task** for the Task.',
        frozen=True,
        title='configTask',
        validate_default=True,
    )
    dependent_on_id: int | None = Field(
        default=None,
        description='The ID of another Task that this Task is dependent upon.',
        title='dependentOnId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    description: str | None = Field(
        default=None,
        description='The **description** for the Task.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    due_date: datetime | None = Field(
        default=None,
        description='The due date of the Task.',
        title='dueDate',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    duration: int | None = Field(
        default=None,
        description='The **duration** for the Task.',
        frozen=True,
        title='duration',
        validate_default=True,
    )
    duration_type: str | None = Field(
        default=None,
        description='The **duration type** for the Task.',
        title='durationType',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The **name** for the Task.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    notes: NotesModel | None = Field(
        default=None,
        description='A list of Notes corresponding to the Task.',
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
    parent_case: CaseModel | None = Field(
        default=None,
        description='The **parent case** for the Task.',
        frozen=True,
        title='parentCase',
        validate_default=True,
    )
    required: bool | None = Field(
        default=None,
        description='Flag indicating whether or not the task is required.',
        title='required',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    status: str | None = Field(
        default=None,
        description='The **status** for the Task.',
        title='status',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    workflow_phase: int | None = Field(
        default=None,
        description='The phase of the workflow.',
        title='workflowPhase',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    workflow_step: int | None = Field(
        default=None,
        description='The step of the workflow.',
        title='workflowStep',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    xid: str | None = Field(
        default=None,
        description='The **xid** for the Task.',
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

    @field_validator('parent_case', mode='before')
    @classmethod
    def _validate_case(cls, v):
        if not v:
            return CaseModel()  # type: ignore
        return v

    @field_validator('notes', mode='before')
    @classmethod
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()  # type: ignore
        return v


class TaskDataModel(
    BaseModel,
    title='Task Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Tasks Data Model"""

    data: list[TaskModel] | None = Field(
        [],
        description='The data for the Tasks.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class TasksModel(
    BaseModel,
    title='Tasks Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Tasks Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[TaskModel] | None = Field(
        [],
        description='The data for the Tasks.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.artifacts.artifact_model import ArtifactsModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.notes.note_model import NotesModel
from tcex.api.tc.v3.security.assignee_model import AssigneeModel
