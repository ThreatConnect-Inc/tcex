"""Workflow Template / Workflow Templates Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class WorkflowTemplatesModel(
    BaseModel,
    title='WorkflowTemplates Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Workflow Templates Model"""

    data: Optional[List['WorkflowTemplateModel']] = Field(
        [],
        description='The data for the WorkflowTemplates.',
        methods=['POST', 'PUT'],
        title='data',
    )


class WorkflowTemplateDataModel(
    BaseModel,
    title='WorkflowTemplate Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Workflow Templates Data Model"""

    data: Optional[List['WorkflowTemplateModel']] = Field(
        [],
        description='The data for the WorkflowTemplates.',
        methods=['POST', 'PUT'],
        title='data',
    )


class WorkflowTemplateModel(
    BaseModel,
    title='WorkflowTemplate Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Workflow Template Model"""

    active: bool = Field(
        None,
        allow_mutation=False,
        description='The **active** for the Workflow Template.',
        read_only=True,
        title='active',
    )
    assignee: Optional['Assignee'] = Field(
        None,
        allow_mutation=False,
        description='The **assignee** for the Workflow Template.',
        read_only=True,
        title='assignee',
    )
    cases: Optional['CasesModel'] = Field(
        None,
        allow_mutation=False,
        description='The **cases** for the Workflow Template.',
        read_only=True,
        title='cases',
    )
    config_artifact: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **config artifact** for the Workflow Template.',
        read_only=True,
        title='configArtifact',
    )
    config_attribute: Optional[dict] = Field(
        None,
        description='The **config attribute** for the Workflow Template.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='configAttribute',
    )
    config_playbook: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **config playbook** for the Workflow Template.',
        read_only=True,
        title='configPlaybook',
    )
    config_task: Optional[dict] = Field(
        None,
        allow_mutation=False,
        description='The **config task** for the Workflow Template.',
        read_only=True,
        title='configTask',
    )
    description: Optional[str] = Field(
        None,
        description='The **description** for the Workflow Template.',
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
        description='The **name** for the Workflow Template.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='name',
    )
    version: Optional[int] = Field(
        None,
        description='The **version** for the Workflow Template.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='version',
    )

    @validator('cases', always=True)
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()
        return v


# first-party
from tcex.api.tc.v3.case_management.assignee import Assignee
from tcex.api.tc.v3.cases.model import CasesModel

# add forward references
WorkflowTemplateDataModel.update_forward_refs()
WorkflowTemplateModel.update_forward_refs()
WorkflowTemplatesModel.update_forward_refs()
