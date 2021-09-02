"""Workflow Event Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils


class WorkflowEventsModel(
    BaseModel,
    title='WorkflowEvents Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Workflow Events Model"""

    data: 'Optional[List[WorkflowEventModel]]' = Field(
        [],
        description='The data for the WorkflowEvent.',
        methods=['POST', 'PUT'],
        title='data',
    )


class WorkflowEventData(
    BaseModel,
    title='WorkflowEvent Data',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Workflow Event Data"""

    data: 'Optional[WorkflowEventModel]' = Field(
        None,
        description='The data for the WorkflowEvent.',
        methods=['POST', 'PUT'],
        title='data',
    )


class WorkflowEventModel(
    BaseModel,
    title='WorkflowEvent Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Workflow Event Model"""

    case_id: Optional[int] = Field(
        None,
        description='The **case id** for the WorkflowEvent.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseXid',
        title='caseId',
        updatable=False,
    )
    case_xid: Optional[str] = Field(
        None,
        description='The **case xid** for the WorkflowEvent.',
        methods=['POST'],
        read_only=False,
        required_alt_field='caseId',
        title='caseXid',
        updatable=False,
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The **date added** for the WorkflowEvent.',
        read_only=True,
        title='dateAdded',
    )
    deleted: bool = Field(
        None,
        allow_mutation=False,
        description='The **deleted** for the WorkflowEvent.',
        read_only=True,
        title='deleted',
    )
    deleted_reason: Optional[str] = Field(
        None,
        description='The reason for deleting the event (required input for DELETE operation only).',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='deletedReason',
    )
    event_date: Optional[datetime] = Field(
        None,
        description='The time that the Event is logged.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='eventDate',
    )
    id: Optional[int] = Field(
        None,
        description='The id of the **Object**.',
        read_only=True,
        title='id',
    )
    link: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **link** for the WorkflowEvent.',
        read_only=True,
        title='link',
    )
    link_text: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **link text** for the WorkflowEvent.',
        read_only=True,
        title='linkText',
    )
    notes: 'Optional[NotesModel]' = Field(
        None,
        description='A list of Notes corresponding to the Event.',
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='notes',
    )
    parent_case: 'Optional[CaseModel]' = Field(
        None,
        allow_mutation=False,
        description='The **parent case** for the WorkflowEvent.',
        read_only=True,
        title='parentCase',
    )
    summary: Optional[str] = Field(
        None,
        description='The **summary** for the WorkflowEvent.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='summary',
    )
    system_generated: bool = Field(
        None,
        allow_mutation=False,
        description='The **system generated** for the WorkflowEvent.',
        read_only=True,
        title='systemGenerated',
    )
    user: 'Optional[UserModel]' = Field(
        None,
        allow_mutation=False,
        description='The **user** for the WorkflowEvent.',
        read_only=True,
        title='user',
    )

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

    @validator('user', always=True)
    def _validate_user(cls, v):
        if not v:
            return UserModel()
        return v


# first-party
from tcex.api.tc.v3.case_management.models.case_model import CaseModel
from tcex.api.tc.v3.case_management.models.note_model import NotesModel
from tcex.api.tc.v3.security.models.user_model import UserModel


# add forward references
WorkflowEventData.update_forward_refs()
WorkflowEventModel.update_forward_refs()
WorkflowEventsModel.update_forward_refs()
