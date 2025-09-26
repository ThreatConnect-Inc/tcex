"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class NoteModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Note Model',
    validate_assignment=True,
):
    """Note Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=True)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    artifact: ArtifactModel | None = Field(
        default=None,
        description='The **artifact** for the Note.',
        frozen=True,
        title='artifact',
        validate_default=True,
    )
    artifact_id: int | None = Field(
        default=None,
        description='The ID of the Artifact on which to apply the Note.',
        title='artifactId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    author: str | None = Field(
        default=None,
        description='The **author** for the Note.',
        frozen=True,
        title='author',
        validate_default=True,
    )
    case_id: int | None = Field(
        default=None,
        description='The **case id** for the Note.',
        title='caseId',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseXid'},
    )
    case_xid: str | None = Field(
        default=None,
        description='The **case xid** for the Note.',
        title='caseXid',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseId'},
    )
    date_added: datetime | None = Field(
        default=None,
        description='The **date added** for the Note.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    edited: bool | None = Field(
        default=None,
        description='The **edited** for the Note.',
        frozen=True,
        title='edited',
        validate_default=True,
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    last_modified: datetime | None = Field(
        default=None,
        description='The **last modified** for the Note.',
        frozen=True,
        title='lastModified',
        validate_default=True,
    )
    parent_case: CaseModel | None = Field(
        default=None,
        description='The **parent case** for the Note.',
        frozen=True,
        title='parentCase',
        validate_default=True,
    )
    summary: str | None = Field(
        default=None,
        description='The **summary** for the Note.',
        frozen=True,
        title='summary',
        validate_default=True,
    )
    task: TaskModel | None = Field(
        default=None,
        description='The **task** for the Note.',
        frozen=True,
        title='task',
        validate_default=True,
    )
    task_id: int | None = Field(
        default=None,
        description='The ID of the Task on which to apply the Note.',
        title='taskId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    task_xid: str | None = Field(
        default=None,
        description='The XID of the Task on which to apply the Note.',
        title='taskXid',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )
    text: str | None = Field(
        default=None,
        description='The **text** for the Note.',
        title='text',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    workflow_event: WorkflowEventModel | None = Field(
        default=None,
        description='The **workflow event** for the Note.',
        frozen=True,
        title='workflowEvent',
        validate_default=True,
    )
    workflow_event_id: int | None = Field(
        default=None,
        description='The ID of the Event on which to apply the Note.',
        title='workflowEventId',
        validate_default=True,
        json_schema_extra={'methods': ['POST']},
    )

    @field_validator('artifact', mode='before')
    @classmethod
    def _validate_artifact(cls, v):
        if not v:
            return ArtifactModel()  # type: ignore
        return v

    @field_validator('parent_case', mode='before')
    @classmethod
    def _validate_case(cls, v):
        if not v:
            return CaseModel()  # type: ignore
        return v

    @field_validator('task', mode='before')
    @classmethod
    def _validate_task(cls, v):
        if not v:
            return TaskModel()  # type: ignore
        return v

    @field_validator('workflow_event', mode='before')
    @classmethod
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
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class NotesModel(
    BaseModel,
    title='Notes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Notes Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[NoteModel] | None = Field(
        [],
        description='The data for the Notes.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.tasks.task_model import TaskModel
from tcex.api.tc.v3.workflow_events.workflow_event_model import WorkflowEventModel
