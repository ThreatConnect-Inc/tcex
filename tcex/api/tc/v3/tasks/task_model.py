"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class TaskModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Task Model',
    validate_assignment=True,
):
    """Task Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    artifacts: 'ArtifactsModel' = Field(
        None,
        description='A list of Artifacts corresponding to the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='artifacts',
    )
    assignee: 'AssigneeModel' = Field(
        None,
        description='The user or group Assignee object for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='assignee',
    )
    case_id: int | None = Field(
        None,
        description='The **case id** for the Task.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseXid',
        title='caseId',
    )
    case_xid: str | None = Field(
        None,
        description='The **case xid** for the Task.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseId',
        title='caseXid',
    )
    completed_by: str | None = Field(
        None,
        allow_mutation=False,
        description='The **completed by** for the Task.',
        read_only=True,
        title='completedBy',
    )
    completed_date: datetime | None = Field(
        None,
        description='The completion date of the Task.',
        methods=['POST'],
        read_only=False,
        title='completedDate',
    )
    config_playbook: str | None = Field(
        None,
        allow_mutation=False,
        description='The **config playbook** for the Task.',
        read_only=True,
        title='configPlaybook',
    )
    config_task: dict | list[dict] | None = Field(
        None,
        allow_mutation=False,
        description='The **config task** for the Task.',
        read_only=True,
        title='configTask',
    )
    dependent_on_id: int | None = Field(
        None,
        description='The ID of another Task that this Task is dependent upon.',
        methods=['POST'],
        read_only=False,
        title='dependentOnId',
    )
    description: str | None = Field(
        None,
        description='The **description** for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='description',
    )
    due_date: datetime | None = Field(
        None,
        description='The due date of the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='dueDate',
    )
    duration: int | None = Field(
        None,
        allow_mutation=False,
        description='The **duration** for the Task.',
        read_only=True,
        title='duration',
    )
    duration_type: str | None = Field(
        None,
        description='The **duration type** for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='durationType',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: str | None = Field(
        None,
        description='The **name** for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    notes: 'NotesModel' = Field(
        None,
        description='A list of Notes corresponding to the Task.',
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
    parent_case: 'CaseModel' = Field(
        None,
        allow_mutation=False,
        description='The **parent case** for the Task.',
        read_only=True,
        title='parentCase',
    )
    required: bool = Field(
        None,
        description='Flag indicating whether or not the task is required.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='required',
    )
    status: str | None = Field(
        None,
        description='The **status** for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='status',
    )
    workflow_phase: int | None = Field(
        None,
        description='The phase of the workflow.',
        methods=['POST'],
        read_only=False,
        title='workflowPhase',
    )
    workflow_step: int | None = Field(
        None,
        description='The step of the workflow.',
        methods=['POST'],
        read_only=False,
        title='workflowStep',
    )
    xid: str | None = Field(
        None,
        description='The **xid** for the Task.',
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

    @validator('parent_case', always=True, pre=True)
    def _validate_case(cls, v):
        if not v:
            return CaseModel()  # type: ignore
        return v

    @validator('notes', always=True, pre=True)
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
        methods=['POST', 'PUT'],
        title='data',
    )


class TasksModel(
    BaseModel,
    title='Tasks Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Tasks Model"""

    _mode_support = PrivateAttr(False)

    data: list[TaskModel] | None = Field(
        [],
        description='The data for the Tasks.',
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
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.notes.note_model import NotesModel
from tcex.api.tc.v3.security.assignee_model import AssigneeModel

# add forward references
TaskDataModel.update_forward_refs()
TaskModel.update_forward_refs()
TasksModel.update_forward_refs()
