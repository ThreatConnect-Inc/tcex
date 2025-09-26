"""TcEx Framework Module"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class WorkflowEventModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='WorkflowEvent Model',
    validate_assignment=True,
):
    """Workflow_Event Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=True)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    case_id: int | None = Field(
        default=None,
        description='The **case id** for the Workflow_Event.',
        title='caseId',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseXid'},
    )
    case_xid: str | None = Field(
        default=None,
        description='The **case xid** for the Workflow_Event.',
        title='caseXid',
        validate_default=True,
        json_schema_extra={'methods': ['POST'], 'required_alt_field': 'caseId'},
    )
    date_added: datetime | None = Field(
        default=None,
        description='The **date added** for the Workflow_Event.',
        frozen=True,
        title='dateAdded',
        validate_default=True,
    )
    deleted: bool | None = Field(
        default=None,
        description='The **deleted** for the Workflow_Event.',
        frozen=True,
        title='deleted',
        validate_default=True,
    )
    deleted_reason: str | None = Field(
        default=None,
        description='The reason for deleting the event (required input for DELETE operation only).',
        title='deletedReason',
        validate_default=True,
        json_schema_extra={'methods': ['DELETE']},
    )
    event_date: datetime | None = Field(
        default=None,
        description='The time that the Event is logged.',
        title='eventDate',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    link: str | None = Field(
        default=None,
        description='The **link** for the Workflow_Event.',
        frozen=True,
        title='link',
        validate_default=True,
    )
    link_text: str | None = Field(
        default=None,
        description='The **link text** for the Workflow_Event.',
        frozen=True,
        title='linkText',
        validate_default=True,
    )
    notes: NotesModel | None = Field(
        default=None,
        description='A list of Notes corresponding to the Event.',
        title='notes',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    parent_case: CaseModel | None = Field(
        default=None,
        description='The **parent case** for the Workflow_Event.',
        frozen=True,
        title='parentCase',
        validate_default=True,
    )
    summary: str | None = Field(
        default=None,
        description='The **summary** for the Workflow_Event.',
        title='summary',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    system_generated: bool | None = Field(
        default=None,
        description='The **system generated** for the Workflow_Event.',
        frozen=True,
        title='systemGenerated',
        validate_default=True,
    )
    user: UserModel | None = Field(
        default=None,
        description='The **user** for the Workflow_Event.',
        frozen=True,
        title='user',
        validate_default=True,
    )

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

    @field_validator('user', mode='before')
    @classmethod
    def _validate_user(cls, v):
        if not v:
            return UserModel()  # type: ignore
        return v


class WorkflowEventDataModel(
    BaseModel,
    title='WorkflowEvent Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Workflow_Events Data Model"""

    data: list[WorkflowEventModel] | None = Field(
        [],
        description='The data for the WorkflowEvents.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class WorkflowEventsModel(
    BaseModel,
    title='WorkflowEvents Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Workflow_Events Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[WorkflowEventModel] | None = Field(
        [],
        description='The data for the WorkflowEvents.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.cases.case_model import CaseModel
from tcex.api.tc.v3.notes.note_model import NotesModel
from tcex.api.tc.v3.security.users.user_model import UserModel
