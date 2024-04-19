"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class NoteModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Note Model',
    validate_assignment=True,
):
    """Note Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    artifact: 'ArtifactModel' = Field(
        None,
        allow_mutation=False,
        description='The **artifact** for the Note.',
        read_only=True,
        title='artifact',
    )
    artifact_id: int | None = Field(
        None,
        description='The ID of the Artifact on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='artifactId',
    )
    author: str | None = Field(
        None,
        allow_mutation=False,
        description='The **author** for the Note.',
        read_only=True,
        title='author',
    )
    case_id: int | None = Field(
        None,
        description='The **case id** for the Note.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseXid',
        title='caseId',
    )
    case_xid: str | None = Field(
        None,
        description='The **case xid** for the Note.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseId',
        title='caseXid',
    )
    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The **date added** for the Note.',
        read_only=True,
        title='dateAdded',
    )
    edited: bool = Field(
        None,
        allow_mutation=False,
        description='The **edited** for the Note.',
        read_only=True,
        title='edited',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    last_modified: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The **last modified** for the Note.',
        read_only=True,
        title='lastModified',
    )
    parent_case: 'CaseModel' = Field(
        None,
        allow_mutation=False,
        description='The **parent case** for the Note.',
        read_only=True,
        title='parentCase',
    )
    summary: str | None = Field(
        None,
        allow_mutation=False,
        description='The **summary** for the Note.',
        read_only=True,
        title='summary',
    )
    task: 'TaskModel' = Field(
        None,
        allow_mutation=False,
        description='The **task** for the Note.',
        read_only=True,
        title='task',
    )
    task_id: int | None = Field(
        None,
        description='The ID of the Task on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='taskId',
    )
    task_xid: str | None = Field(
        None,
        description='The XID of the Task on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='taskXid',
    )
    text: str | None = Field(
        None,
        description='The **text** for the Note.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='text',
    )
    workflow_event: 'WorkflowEventModel' = Field(
        None,
        allow_mutation=False,
        description='The **workflow event** for the Note.',
        read_only=True,
        title='workflowEvent',
    )
    workflow_event_id: int | None = Field(
        None,
        description='The ID of the Event on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='workflowEventId',
    )

    @validator('artifact', always=True, pre=True)
    def _validate_artifact(cls, v):
        if not v:
            return ArtifactModel()  # type: ignore
        return v

    @validator('parent_case', always=True, pre=True)
    def _validate_case(cls, v):
        if not v:
            return CaseModel()  # type: ignore
        return v

    @validator('task', always=True, pre=True)
    def _validate_task(cls, v):
        if not v:
            return TaskModel()  # type: ignore
        return v

    @validator('workflow_event', always=True, pre=True)
    def _validate_workflow_event(cls, v):
        if not v:
            return WorkflowEventModel()  # type: ignore
        return v


class NoteDataModel(
    BaseModel,
    title='Note Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Notes Data Model"""

    data: list[NoteModel] | None = Field(
        [],
        description='The data for the Notes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class NotesModel(
    BaseModel,
    title='Notes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Notes Model"""

    _mode_support = PrivateAttr(False)

    data: list[NoteModel] | None = Field(
        [],
        description='The data for the Notes.',
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
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.tasks.task_model import TaskModel
from tcex.api.tc.v3.workflow_events.workflow_event_model import WorkflowEventModel

# add forward references
NoteDataModel.update_forward_refs()
NoteModel.update_forward_refs()
NotesModel.update_forward_refs()
