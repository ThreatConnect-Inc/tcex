"""TcEx Framework Module"""
# pylint: disable=no-member,no-self-argument,wrong-import-position
# standard library
from datetime import datetime

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class GroupAttributeModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='GroupAttribute Model',
    validate_assignment=True,
):
    """Group_Attribute Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    created_by: 'UserModel' = Field(
        None,
        allow_mutation=False,
        description='The **created by** for the Group_Attribute.',
        read_only=True,
        title='createdBy',
    )
    date_added: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    default: bool = Field(
        None,
        description=(
            'A flag indicating that this is the default attribute of its type within the object. '
            'Only applies to certain attribute and data types.'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='default',
    )
    group: 'GroupModel' = Field(
        None,
        allow_mutation=False,
        description='Details of group associated with attribute.',
        read_only=True,
        title='group',
    )
    group_id: int | None = Field(
        None,
        description='Group associated with attribute.',
        methods=['POST'],
        read_only=False,
        title='groupId',
    )
    id: int | None = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    last_modified: datetime | None = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was last modified.',
        read_only=True,
        title='lastModified',
    )
    pinned: bool = Field(
        None,
        description='A flag indicating that the attribute has been noted for importance.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='pinned',
    )
    security_labels: 'SecurityLabelsModel' = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityLabels',
    )
    source: str | None = Field(
        None,
        description='The attribute source.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='source',
    )
    type: str | None = Field(
        None,
        description='The attribute type.',
        methods=['POST'],
        read_only=False,
        title='type',
    )
    value: str | None = Field(
        None,
        description='The attribute value.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='value',
    )

    @validator('group', always=True, pre=True)
    def _validate_group(cls, v):
        if not v:
            return GroupModel()  # type: ignore
        return v

    @validator('security_labels', always=True, pre=True)
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()  # type: ignore
        return v

    @validator('created_by', always=True, pre=True)
    def _validate_user(cls, v):
        if not v:
            return UserModel()  # type: ignore
        return v


class GroupAttributeDataModel(
    BaseModel,
    title='GroupAttribute Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Group_Attributes Data Model"""

    data: list[GroupAttributeModel] | None = Field(
        [],
        description='The data for the GroupAttributes.',
        methods=['POST', 'PUT'],
        title='data',
    )


class GroupAttributesModel(
    BaseModel,
    title='GroupAttributes Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Group_Attributes Model"""

    _mode_support = PrivateAttr(True)

    data: list[GroupAttributeModel] | None = Field(
        [],
        description='The data for the GroupAttributes.',
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
from tcex.api.tc.v3.groups.group_model import GroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel

# add forward references
GroupAttributeDataModel.update_forward_refs()
GroupAttributeModel.update_forward_refs()
GroupAttributesModel.update_forward_refs()
