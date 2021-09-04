"""Case / Cases Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class CasesModel(
    BaseModel,
    title='Cases Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Cases Model"""

    data: Optional[List['CaseModel']] = Field(
        [],
        description='The data for the Cases.',
        methods=['POST', 'PUT'],
        title='data',
    )


class CaseDataModel(
    BaseModel,
    title='Case Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Cases Data Model"""

    data: Optional[List['CaseModel']] = Field(
        [],
        description='The data for the Cases.',
        methods=['POST', 'PUT'],
        title='data',
    )


class CaseModel(
    BaseModel,
    title='Case Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Case Model"""

    artifacts: Optional['ArtifactsModel'] = Field(
        None,
        description='A list of Artifacts corresponding to the Case.',
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='artifacts',
    )
    assignee: Optional['Assignee'] = Field(
        None,
        description='The user or group Assignee object for the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='assignee',
    )
    attributes: Optional['AttributesModel'] = Field(
        None,
        description='A list of Attributes corresponding to the Case.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='attributes',
    )
    created_by: Optional['UserModel'] = Field(
        None,
        allow_mutation=False,
        description='The **created by** for the Case.',
        read_only=True,
        title='createdBy',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Case was first created.',
        read_only=True,
        title='dateAdded',
    )
    description: Optional[str] = Field(
        None,
        description='The description of the Case.',
        methods=['POST', 'PUT'],
        max_length=1500,
        min_length=0,
        read_only=False,
        title='description',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        description='The name of the Case.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='name',
    )
    notes: Optional['NotesModel'] = Field(
        None,
        description='A list of Notes corresponding to the Case.',
        methods=['POST', 'PUT'],
        max_size=1000,
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
    related: Optional['CasesModel'] = Field(
        None,
        allow_mutation=False,
        description='The **related** for the Case.',
        read_only=True,
        title='related',
    )
    resolution: Optional[str] = Field(
        None,
        description='The Case resolution.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='resolution',
    )
    severity: Optional[str] = Field(
        None,
        description='The Case severity.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='severity',
    )
    status: Optional[str] = Field(
        None,
        description='The Case status.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='status',
    )
    tags: Optional['TagsModel'] = Field(
        None,
        description=(
            'A list of Tags corresponding to the Case (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='tags',
    )
    tasks: Optional['TasksModel'] = Field(
        None,
        description='A list of Tasks corresponding to the Case.',
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='tasks',
    )
    user_access: Optional['UsersModel'] = Field(
        None,
        description=(
            'A list of Users that, when defined, are the only ones allowed to view or edit the '
            'Case.'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='userAccess',
    )
    workflow_events: Optional['WorkflowEventsModel'] = Field(
        None,
        description='A list of workflowEvents (timeline) corresponding to the Case.',
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='workflowEvents',
    )
    workflow_template: Optional['WorkflowTemplateModel'] = Field(
        None,
        description='The Template that the Case is populated by.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='workflowTemplate',
    )
    xid: Optional[str] = Field(
        None,
        description='The **xid** for the Case.',
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

    @validator('attributes', always=True)
    def _validate_attributes(cls, v):
        if not v:
            return AttributesModel()
        return v

    @validator('related', always=True)
    def _validate_related(cls, v):
        if not v:
            return CasesModel()
        return v

    @validator('notes', always=True)
    def _validate_notes(cls, v):
        if not v:
            return NotesModel()
        return v

    @validator('tags', always=True)
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()
        return v

    @validator('tasks', always=True)
    def _validate_tasks(cls, v):
        if not v:
            return TasksModel()
        return v

    @validator('created_by', always=True)
    def _validate_created_by(cls, v):
        if not v:
            return UserModel()
        return v

    @validator('user_access', always=True)
    def _validate_user_access(cls, v):
        if not v:
            return UsersModel()
        return v

    @validator('workflow_events', always=True)
    def _validate_workflow_events(cls, v):
        if not v:
            return WorkflowEventsModel()
        return v

    @validator('workflow_template', always=True)
    def _validate_workflow_template(cls, v):
        if not v:
            return WorkflowTemplateModel()
        return v


# first-party
from tcex.api.tc.v3.artifacts.model import ArtifactsModel
from tcex.api.tc.v3.case_management.assignee import Assignee
from tcex.api.tc.v3.case_management.models.attribute_model import AttributesModel
from tcex.api.tc.v3.notes.model import NotesModel
from tcex.api.tc.v3.tags.model import TagsModel
from tcex.api.tc.v3.tasks.model import TasksModel
from tcex.api.tc.v3.users.model import UserModel
from tcex.api.tc.v3.users.model import UsersModel
from tcex.api.tc.v3.workflow_events.model import WorkflowEventsModel
from tcex.api.tc.v3.workflow_templates.model import WorkflowTemplateModel

# add forward references
CaseDataModel.update_forward_refs()
CaseModel.update_forward_refs()
CasesModel.update_forward_refs()
