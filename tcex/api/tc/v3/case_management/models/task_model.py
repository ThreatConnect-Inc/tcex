"""Task Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils


class TasksModel(
    BaseModel,
    title='Tasks Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Tasks Model"""

    data: 'Optional[List[TaskModel]]' = Field(
        [],
        description='The data for the Task.',
        methods=['POST', 'PUT'],
        title='data',
    )


class TaskData(
    BaseModel,
    title='Task Data',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Task Data"""

    data: 'Optional[TaskModel]' = Field(
        None,
        description='The data for the Task.',
        methods=['POST', 'PUT'],
        title='data',
    )


class TaskModel(
    BaseModel,
    title='Task Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Task Model"""

    artifacts: Optional['ArtifactsModel'] = Field(
        None,
        description='A list of Artifacts corresponding to the Task.',
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='artifacts',
    )
    assignee: Optional['Assignee'] = Field(
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
        updatable=False,
    )
    case_xid: Optional[str] = Field(
        None,
        description='The **case xid** for the Task.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseId',
        title='caseXid',
        updatable=False,
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
        updatable=False,
    )
    config_playbook: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **config playbook** for the Task.',
        read_only=True,
        title='configPlaybook',
    )
    config_task: Optional[dict] = Field(
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
        updatable=False,
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
    id: Optional[int] = Field(
        None,
        description='The id of the **Object**.',
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
        max_size=1000,
        read_only=False,
        title='notes',
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
        read_only=False,
        title='workflowPhase',
        updatable=False,
    )
    workflow_step: Optional[int] = Field(
        None,
        description='The step of the workflow.',
        methods=['POST'],
        read_only=False,
        title='workflowStep',
        updatable=False,
    )
    xid: Optional[str] = Field(
        None,
        description='The **xid** for the Task.',
        methods=['POST'],
        max_length=100,
        min_length=10,
        read_only=False,
        title='xid',
        updatable=False,
    )

    @validator('artifacts', always=True)
    def _validate_artifacts(cls, v):
        if not v:
            return ArtifactsModel()
        return v

    @validator('parent_case', always=True)
    def _validate_parent_case(cls, v):
        if not v:
            return CaseModel()
        return v

    @validator('notes', always=True)
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()
        return v


# first-party
from tcex.api.tc.v3.case_management.assignee import Assignee
from tcex.api.tc.v3.case_management.models.artifact_model import ArtifactsModel
from tcex.api.tc.v3.case_management.models.case_model import CaseModel
from tcex.api.tc.v3.case_management.models.note_model import NotesModel


# add forward references
TaskData.update_forward_refs()
TaskModel.update_forward_refs()
TasksModel.update_forward_refs()
