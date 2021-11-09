"""Note / Notes Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

# json-encoder
json_encoders = {datetime: lambda v: v.isoformat()}


class NotesModel(
    BaseModel,
    title='Notes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Notes Model"""

    data: Optional[List['NoteModel']] = Field(
        [],
        description='The data for the Notes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class NoteDataModel(
    BaseModel,
    title='Note Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Notes Data Model"""

    data: Optional[List['NoteModel']] = Field(
        [],
        description='The data for the Notes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class NoteModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Note Model',
    validate_assignment=True,
    json_encoders=json_encoders,
):
    """Note Model"""

    # slot attributes are not added to dict()/json()
    __slot__ = ('_privates_',)

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(**kwargs)
        super().__setattr__('_privates_', {'_modified_': 0})

    def __setattr__(self, name, value):
        """Update modified property on any update."""
        super().__setattr__('_privates_', {'_modified_': self.privates.get('_modified_', 0) + 1})
        super().__setattr__(name, value)

    @property
    def modified(self):
        """Return int value of modified (> 0 means modified)."""
        return self._privates_.get('_modified_', 0)

    @property
    def privates(self):
        """Return privates dict."""
        return self._privates_

    artifact: Optional['ArtifactModel'] = Field(
        None,
        allow_mutation=False,
        description='The **artifact** for the Note.',
        read_only=True,
        title='artifact',
    )
    artifact_id: Optional[int] = Field(
        None,
        description='The ID of the Artifact on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='artifactId',
        updatable=False,
    )
    author: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **author** for the Note.',
        read_only=True,
        title='author',
    )
    case_id: Optional[int] = Field(
        None,
        description='The **case id** for the Note.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseXid',
        title='caseId',
        updatable=False,
    )
    case_xid: Optional[str] = Field(
        None,
        description='The **case xid** for the Note.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseId',
        title='caseXid',
        updatable=False,
    )
    date_added: Optional[datetime] = Field(
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
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    last_modified: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The **last modified** for the Note.',
        read_only=True,
        title='lastModified',
    )
    parent_case: Optional['CaseModel'] = Field(
        None,
        allow_mutation=False,
        description='The **parent case** for the Note.',
        read_only=True,
        title='parentCase',
    )
    summary: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **summary** for the Note.',
        read_only=True,
        title='summary',
    )
    task: Optional['TaskModel'] = Field(
        None,
        allow_mutation=False,
        description='The **task** for the Note.',
        read_only=True,
        title='task',
    )
    task_id: Optional[int] = Field(
        None,
        description='The ID of the Task on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='taskId',
        updatable=False,
    )
    task_xid: Optional[str] = Field(
        None,
        description='The XID of the Task on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='taskXid',
        updatable=False,
    )
    text: Optional[str] = Field(
        None,
        description='The **text** for the Note.',
        methods=['POST', 'PUT'],
        max_length=65500,
        min_length=1,
        read_only=False,
        title='text',
    )
    workflow_event: Optional['WorkflowEventModel'] = Field(
        None,
        allow_mutation=False,
        description='The **workflow event** for the Note.',
        read_only=True,
        title='workflowEvent',
    )
    workflow_event_id: Optional[int] = Field(
        None,
        description='The ID of the Event on which to apply the Note.',
        methods=['POST'],
        read_only=False,
        title='workflowEventId',
        updatable=False,
    )

    @validator('artifact', always=True)
    def _validate_artifact(cls, v):
        if not v:
            return ArtifactModel()
        return v

    @validator('parent_case', always=True)
    def _validate_parent_case(cls, v):
        if not v:
            return CaseModel()
        return v

    @validator('task', always=True)
    def _validate_task(cls, v):
        if not v:
            return TaskModel()
        return v

    @validator('workflow_event', always=True)
    def _validate_workflow_event(cls, v):
        if not v:
            return WorkflowEventModel()
        return v


# first-party
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.tasks.task_model import TaskModel
from tcex.api.tc.v3.workflow_events.workflow_event_model import WorkflowEventModel

# add forward references
NoteDataModel.update_forward_refs()
NoteModel.update_forward_refs()
NotesModel.update_forward_refs()
