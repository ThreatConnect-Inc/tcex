"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class WorkflowTemplateModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='WorkflowTemplate Model',
    validate_assignment=True,
):
    """Workflow_Template Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(True)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    active: bool = Field(
        None,
        allow_mutation=False,
        description='The **active** for the Workflow_Template.',
        read_only=True,
        title='active',
    )
    assignee: 'AssigneeModel' = Field(
        None,
        allow_mutation=False,
        description='The **assignee** for the Workflow_Template.',
        read_only=True,
        title='assignee',
    )
    cases: 'CasesModel' = Field(
        None,
        allow_mutation=False,
        description='The **cases** for the Workflow_Template.',
        read_only=True,
        title='cases',
    )
    config_artifact: str | None = Field(
        None,
        allow_mutation=False,
        description='The **config artifact** for the Workflow_Template.',
        read_only=True,
        title='configArtifact',
    )
    config_attribute: dict | list[dict] | None = Field(
        None,
        description='The **config attribute** for the Workflow_Template.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='configAttribute',
    )
    config_playbook: str | None = Field(
        None,
        allow_mutation=False,
        description='The **config playbook** for the Workflow_Template.',
        read_only=True,
        title='configPlaybook',
    )
    config_task: dict | list[dict] | None = Field(
        None,
        allow_mutation=False,
        description='The **config task** for the Workflow_Template.',
        read_only=True,
        title='configTask',
    )
    description: str | None = Field(
        None,
        description='The **description** for the Workflow_Template.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='description',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: str | None = Field(
        None,
        description='The **name** for the Workflow_Template.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    owner: str | None = Field(
        None,
        allow_mutation=False,
        description='The name of the Owner of the Case.',
        read_only=True,
        title='owner',
    )
    owner_id: int | None = Field(
        None,
        allow_mutation=False,
        description='The name of the Owner of the Case.',
        read_only=True,
        title='ownerId',
    )
    version: int | None = Field(
        None,
        description='The **version** for the Workflow_Template.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='version',
    )

    @validator('assignee', always=True, pre=True)
    def _validate_assignee(cls, v):
        if not v:
            return AssigneeModel()  # type: ignore
        return v

    @validator('cases', always=True, pre=True)
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
        methods=['POST', 'PUT'],
        title='data',
    )


class WorkflowTemplatesModel(
    BaseModel,
    title='WorkflowTemplates Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Workflow_Templates Model"""

    _mode_support = PrivateAttr(False)

    data: list[WorkflowTemplateModel] | None = Field(
        [],
        description='The data for the WorkflowTemplates.',
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
from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.security.assignee_model import AssigneeModel

# add forward references
WorkflowTemplateDataModel.update_forward_refs()
WorkflowTemplateModel.update_forward_refs()
WorkflowTemplatesModel.update_forward_refs()
