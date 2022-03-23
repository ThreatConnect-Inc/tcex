"""Task / Tasks Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional, Union

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class TasksModel(
    BaseModel,
    title='Tasks Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Tasks Model"""

    _mode_support = PrivateAttr(False)

    data: Optional[List['TaskModel']] = Field(
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


class TaskDataModel(
    BaseModel,
    title='Task Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Tasks Data Model"""

    data: Optional[List['TaskModel']] = Field(
        [],
        description='The data for the Tasks.',
        methods=['POST', 'PUT'],
        title='data',
    )


class TaskModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Task Model',
    validate_assignment=True,
):
    """Task Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    artifacts: Optional['ArtifactsModel'] = Field(
        None,
        description='A list of Artifacts corresponding to the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='artifacts',
    )
    assignee: Optional['AssigneeModel'] = Field(
        None,
        description='The user or group Assignee object for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='assignee',
    )
    case_id: Optional[int] = Field(
        None,
        description='The **case id** for the Task.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseXid',
        title='caseId',
    )
    case_xid: Optional[str] = Field(
        None,
        description='The **case xid** for the Task.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseId',
        title='caseXid',
    )
    completed_by: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **completed by** for the Task.',
        read_only=True,
        title='completedBy',
    )
    completed_date: Optional[datetime] = Field(
        None,
        description='The completion date of the Task.',
        methods=['POST'],
        read_only=False,
        title='completedDate',
    )
    config_playbook: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **config playbook** for the Task.',
        read_only=True,
        title='configPlaybook',
    )
    config_task: Union[Optional[dict], Optional[List[dict]]] = Field(
        None,
        allow_mutation=False,
        description='The **config task** for the Task.',
        read_only=True,
        title='configTask',
    )
    dependent_on_id: Optional[int] = Field(
        None,
        description='The ID of another Task that this Task is dependent upon.',
        methods=['POST'],
        read_only=False,
        title='dependentOnId',
    )
    description: Optional[str] = Field(
        None,
        description='The **description** for the Task.',
        methods=['POST', 'PUT'],
        max_length=1500,
        min_length=0,
        read_only=False,
        title='description',
    )
    due_date: Optional[datetime] = Field(
        None,
        description='The due date of the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='dueDate',
    )
    duration: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The **duration** for the Task.',
        read_only=True,
        title='duration',
    )
    duration_type: Optional[str] = Field(
        None,
        description='The **duration type** for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='durationType',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        description='The **name** for the Task.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='name',
    )
    notes: Optional['NotesModel'] = Field(
        None,
        description='A list of Notes corresponding to the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='notes',
    )
    owner: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The name of the Owner of the Case.',
        read_only=True,
        title='owner',
    )
    parent_case: Optional['CaseModel'] = Field(
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
    status: Optional[str] = Field(
        None,
        description='The **status** for the Task.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='status',
    )
    workflow_phase: Optional[int] = Field(
        None,
        description='The phase of the workflow.',
        methods=['POST'],
        maximum=127,
        minimum=0,
        read_only=False,
        title='workflowPhase',
    )
    workflow_step: Optional[int] = Field(
        None,
        description='The step of the workflow.',
        methods=['POST'],
        maximum=127,
        minimum=1,
        read_only=False,
        title='workflowStep',
    )
    xid: Optional[str] = Field(
        None,
        description='The **xid** for the Task.',
        methods=['POST'],
        max_length=100,
        min_length=10,
        read_only=False,
        title='xid',
    )

    @validator('artifacts', always=True)
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()
        return v

    @validator('assignee', always=True)
    def _validate_assignee(cls, v):
        if not v:
            return AssigneeModel()
        return v

    @validator('parent_case', always=True)
    def _validate_case(cls, v):
        if not v:
            return CaseModel()
        return v

    @validator('notes', always=True)
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()
        return v


# first-party
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactsModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.notes.note_model import NotesModel
from tcex.api.tc.v3.security.assignee_model import AssigneeModel

# add forward references
TaskDataModel.update_forward_refs()
TaskModel.update_forward_refs()
TasksModel.update_forward_refs()
