"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class WorkflowTemplateModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='WorkflowTemplate Model',
    validate_assignment=True,
):
    """Workflow_Template Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=True)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    active: bool | None = Field(
        default=None,
        description='The **active** for the Workflow_Template.',
        frozen=True,
        title='active',
        validate_default=True,
    )
    assignee: AssigneeModel | None = Field(
        default=None,
        description='The **assignee** for the Workflow_Template.',
        frozen=True,
        title='assignee',
        validate_default=True,
    )
    cases: CasesModel | None = Field(
        default=None,
        description='The **cases** for the Workflow_Template.',
        frozen=True,
        title='cases',
        validate_default=True,
    )
    config_artifact: str | None = Field(
        default=None,
        description='The **config artifact** for the Workflow_Template.',
        frozen=True,
        title='configArtifact',
        validate_default=True,
    )
    config_attribute: dict | list[dict] | None = Field(
        default=None,
        description='The **config attribute** for the Workflow_Template.',
        title='configAttribute',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    config_playbook: str | None = Field(
        default=None,
        description='The **config playbook** for the Workflow_Template.',
        frozen=True,
        title='configPlaybook',
        validate_default=True,
    )
    config_task: dict | list[dict] | None = Field(
        default=None,
        description='The **config task** for the Workflow_Template.',
        frozen=True,
        title='configTask',
        validate_default=True,
    )
    description: str | None = Field(
        default=None,
        description='The **description** for the Workflow_Template.',
        title='description',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The **name** for the Workflow_Template.',
        title='name',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
    owner: str | None = Field(
        default=None,
        description='The name of the Owner of the Case.',
        frozen=True,
        title='owner',
        validate_default=True,
    )
    owner_id: int | None = Field(
        default=None,
        description='The name of the Owner of the Case.',
        frozen=True,
        title='ownerId',
        validate_default=True,
    )
    version: int | None = Field(
        default=None,
        description='The **version** for the Workflow_Template.',
        title='version',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )

    @field_validator('assignee', mode='before')
    @classmethod
    def _validate_assignee(cls, v):
        if not v:
            return AssigneeModel()  # type: ignore
        return v

    @field_validator('cases', mode='before')
    @classmethod
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()  # type: ignore
        return v


class WorkflowTemplateDataModel(
    BaseModel,
    title='WorkflowTemplate Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Workflow_Templates Data Model"""

    data: list[WorkflowTemplateModel] | None = Field(
        [],
        description='The data for the WorkflowTemplates.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class WorkflowTemplatesModel(
    BaseModel,
    title='WorkflowTemplates Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Workflow_Templates Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[WorkflowTemplateModel] | None = Field(
        [],
        description='The data for the WorkflowTemplates.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.security.assignee_model import AssigneeModel
