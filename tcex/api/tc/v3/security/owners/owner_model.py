"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class OwnerModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='Owner Model',
    validate_assignment=True,
):
    """Owner Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: str | None = Field(
        None,
        allow_mutation=False,
        description='The name of the owner.',
        read_only=True,
        title='name',
    )
    owner_role: str | None = Field(
        None,
        allow_mutation=False,
        description='The user\'s role within the owner.',
        read_only=True,
        title='ownerRole',
    )
    perm_apps: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to run/edit Apps.',
        read_only=True,
        title='permApps',
    )
    perm_artifact: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to access an Artifact.',
        read_only=True,
        title='permArtifact',
    )
    perm_attribute: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Attributes.',
        read_only=True,
        title='permAttribute',
    )
    perm_attribute_type: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Attribute Types.',
        read_only=True,
        title='permAttributeType',
    )
    perm_case_tag: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Tag.',
        read_only=True,
        title='permCaseTag',
    )
    perm_comment: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Comment.',
        read_only=True,
        title='permComment',
    )
    perm_copy_data: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Copy Data.',
        read_only=True,
        title='permCopyData',
    )
    perm_group: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Groups.',
        read_only=True,
        title='permGroup',
    )
    perm_indicator: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Indicators.',
        read_only=True,
        title='permIndicator',
    )
    perm_invite: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to modify friends.',
        read_only=True,
        title='permInvite',
    )
    perm_members: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Members.',
        read_only=True,
        title='permMembers',
    )
    perm_playbooks: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used with Playbooks.',
        read_only=True,
        title='permPlaybooks',
    )
    perm_playbooks_execute: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to execute Playbooks.',
        read_only=True,
        title='permPlaybooksExecute',
    )
    perm_post: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Posts.',
        read_only=True,
        title='permPost',
    )
    perm_publish: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to access Publications.',
        read_only=True,
        title='permPublish',
    )
    perm_security_label: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Security Labels.',
        read_only=True,
        title='permSecurityLabel',
    )
    perm_settings: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Organization Settings.',
        read_only=True,
        title='permSettings',
    )
    perm_tag: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Tags.',
        read_only=True,
        title='permTag',
    )
    perm_task: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Task.',
        read_only=True,
        title='permTask',
    )
    perm_timeline: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Timeline.',
        read_only=True,
        title='permTimeline',
    )
    perm_track: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Tracks.',
        read_only=True,
        title='permTrack',
    )
    perm_users: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to User Settings.',
        read_only=True,
        title='permUsers',
    )
    perm_victim: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Victims.',
        read_only=True,
        title='permVictim',
    )
    perm_workflow_template: str | None = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Workflow Templates.',
        read_only=True,
        title='permWorkflowTemplate',
    )
    type: str | None = Field(
        None,
        allow_mutation=False,
        description='The owner type. Possible values: Organization, Community, Source.',
        read_only=True,
        title='type',
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
        methods=['POST', 'PUT'],
        title='data',
    )


class OwnersModel(
    BaseModel,
    title='Owners Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Owners Model"""

    _mode_support = PrivateAttr(False)

    data: list[OwnerModel] | None = Field(
        [],
        description='The data for the Owners.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


# add forward references
OwnerDataModel.update_forward_refs()
OwnerModel.update_forward_refs()
OwnersModel.update_forward_refs()
