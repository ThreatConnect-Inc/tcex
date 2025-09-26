"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class OwnerModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='Owner Model',
    validate_assignment=True,
):
    """Owner Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The name of the owner.',
        frozen=True,
        title='name',
        validate_default=True,
    )
    owner_role: str | None = Field(
        default=None,
        description="The user's role within the owner.",
        frozen=True,
        title='ownerRole',
        validate_default=True,
    )
    perm_apps: str | None = Field(
        default=None,
        description='Permission is used for access to run/edit Apps.',
        frozen=True,
        title='permApps',
        validate_default=True,
    )
    perm_artifact: str | None = Field(
        default=None,
        description='Permission used to access an Artifact.',
        frozen=True,
        title='permArtifact',
        validate_default=True,
    )
    perm_attribute: str | None = Field(
        default=None,
        description='Permission is used for access to Attributes.',
        frozen=True,
        title='permAttribute',
        validate_default=True,
    )
    perm_attribute_type: str | None = Field(
        default=None,
        description='Permission is used for access to Attribute Types.',
        frozen=True,
        title='permAttributeType',
        validate_default=True,
    )
    perm_case_tag: str | None = Field(
        default=None,
        description='Permission used to access a Tag.',
        frozen=True,
        title='permCaseTag',
        validate_default=True,
    )
    perm_comment: str | None = Field(
        default=None,
        description='Permission used to access a Comment.',
        frozen=True,
        title='permComment',
        validate_default=True,
    )
    perm_copy_data: str | None = Field(
        default=None,
        description='Permission is used for access to Copy Data.',
        frozen=True,
        title='permCopyData',
        validate_default=True,
    )
    perm_group: str | None = Field(
        default=None,
        description='Permission is used for access to Groups.',
        frozen=True,
        title='permGroup',
        validate_default=True,
    )
    perm_indicator: str | None = Field(
        default=None,
        description='Permission is used for access to Indicators.',
        frozen=True,
        title='permIndicator',
        validate_default=True,
    )
    perm_invite: str | None = Field(
        default=None,
        description='Permission is used for access to modify friends.',
        frozen=True,
        title='permInvite',
        validate_default=True,
    )
    perm_members: str | None = Field(
        default=None,
        description='Permission is used for access to Members.',
        frozen=True,
        title='permMembers',
        validate_default=True,
    )
    perm_playbooks: str | None = Field(
        default=None,
        description='Permission used with Playbooks.',
        frozen=True,
        title='permPlaybooks',
        validate_default=True,
    )
    perm_playbooks_execute: str | None = Field(
        default=None,
        description='Permission used to execute Playbooks.',
        frozen=True,
        title='permPlaybooksExecute',
        validate_default=True,
    )
    perm_post: str | None = Field(
        default=None,
        description='Permission is used for access to Posts.',
        frozen=True,
        title='permPost',
        validate_default=True,
    )
    perm_publish: str | None = Field(
        default=None,
        description='Permission used to access Publications.',
        frozen=True,
        title='permPublish',
        validate_default=True,
    )
    perm_security_label: str | None = Field(
        default=None,
        description='Permission is used for access to Security Labels.',
        frozen=True,
        title='permSecurityLabel',
        validate_default=True,
    )
    perm_settings: str | None = Field(
        default=None,
        description='Permission is used for access to Organization Settings.',
        frozen=True,
        title='permSettings',
        validate_default=True,
    )
    perm_tag: str | None = Field(
        default=None,
        description='Permission is used for access to Tags.',
        frozen=True,
        title='permTag',
        validate_default=True,
    )
    perm_task: str | None = Field(
        default=None,
        description='Permission used to access a Task.',
        frozen=True,
        title='permTask',
        validate_default=True,
    )
    perm_timeline: str | None = Field(
        default=None,
        description='Permission used to access a Timeline.',
        frozen=True,
        title='permTimeline',
        validate_default=True,
    )
    perm_users: str | None = Field(
        default=None,
        description='Permission is used for access to User Settings.',
        frozen=True,
        title='permUsers',
        validate_default=True,
    )
    perm_victim: str | None = Field(
        default=None,
        description='Permission is used for access to Victims.',
        frozen=True,
        title='permVictim',
        validate_default=True,
    )
    perm_workflow_template: str | None = Field(
        default=None,
        description='Permission used to access a Workflow Templates.',
        frozen=True,
        title='permWorkflowTemplate',
        validate_default=True,
    )
    type: str | None = Field(
        default=None,
        description='The owner type. Possible values: Organization, Community, Source.',
        frozen=True,
        title='type',
        validate_default=True,
    )


class OwnerDataModel(
    BaseModel,
    title='Owner Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Owners Data Model"""

    data: list[OwnerModel] | None = Field(
        [],
        description='The data for the Owners.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class OwnersModel(
    BaseModel,
    title='Owners Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Owners Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[OwnerModel] | None = Field(
        [],
        description='The data for the Owners.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
OwnerDataModel.model_rebuild()
OwnerModel.model_rebuild()
OwnersModel.model_rebuild()
