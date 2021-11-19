"""Owner / Owners Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class OwnersModel(
    BaseModel,
    title='Owners Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Owners Model"""

    _mode_support = PrivateAttr(False)

    data: Optional[List['OwnerModel']] = Field(
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


class OwnerDataModel(
    BaseModel,
    title='Owner Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Owners Data Model"""

    data: Optional[List['OwnerModel']] = Field(
        [],
        description='The data for the Owners.',
        methods=['POST', 'PUT'],
        title='data',
    )


class OwnerModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Owner Model',
    validate_assignment=True,
):
    """Owner Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The name of the owner.',
        read_only=True,
        title='name',
    )
    owner_role: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The user\'s role within the owner.',
        read_only=True,
        title='ownerRole',
    )
    perm_apps: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to run/edit Apps.',
        read_only=True,
        title='permApps',
    )
    perm_artifact: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to access an Artifact.',
        read_only=True,
        title='permArtifact',
    )
    perm_attribute: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Attributes.',
        read_only=True,
        title='permAttribute',
    )
    perm_attribute_type: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Attribute Types.',
        read_only=True,
        title='permAttributeType',
    )
    perm_case_tag: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Tag.',
        read_only=True,
        title='permCaseTag',
    )
    perm_comment: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Comment.',
        read_only=True,
        title='permComment',
    )
    perm_copy_data: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Copy Data.',
        read_only=True,
        title='permCopyData',
    )
    perm_group: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Groups.',
        read_only=True,
        title='permGroup',
    )
    perm_indicator: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Indicators.',
        read_only=True,
        title='permIndicator',
    )
    perm_invite: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to modify friends.',
        read_only=True,
        title='permInvite',
    )
    perm_members: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Members.',
        read_only=True,
        title='permMembers',
    )
    perm_playbooks: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used with Playbooks.',
        read_only=True,
        title='permPlaybooks',
    )
    perm_playbooks_execute: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to execute Playbooks.',
        read_only=True,
        title='permPlaybooksExecute',
    )
    perm_post: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Posts.',
        read_only=True,
        title='permPost',
    )
    perm_publish: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to access Publications.',
        read_only=True,
        title='permPublish',
    )
    perm_security_label: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Security Labels.',
        read_only=True,
        title='permSecurityLabel',
    )
    perm_settings: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Organization Settings.',
        read_only=True,
        title='permSettings',
    )
    perm_tag: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Tags.',
        read_only=True,
        title='permTag',
    )
    perm_task: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Task.',
        read_only=True,
        title='permTask',
    )
    perm_timeline: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Timeline.',
        read_only=True,
        title='permTimeline',
    )
    perm_track: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Tracks.',
        read_only=True,
        title='permTrack',
    )
    perm_users: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to User Settings.',
        read_only=True,
        title='permUsers',
    )
    perm_victim: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission is used for access to Victims.',
        read_only=True,
        title='permVictim',
    )
    perm_workflow_template: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Permission used to access a Workflow Templates.',
        read_only=True,
        title='permWorkflowTemplate',
    )
    type: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The owner type. Possible values: Organization, Community, Source.',
        read_only=True,
        title='type',
    )


# add forward references
OwnerDataModel.update_forward_refs()
OwnerModel.update_forward_refs()
OwnersModel.update_forward_refs()
