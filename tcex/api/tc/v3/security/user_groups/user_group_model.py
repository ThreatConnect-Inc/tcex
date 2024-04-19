"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class UserGroupModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='UserGroup Model',
    validate_assignment=True,
):
    """User_Group Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    description: str | None = Field(
        None,
        allow_mutation=False,
        description='The **description** for the User_Group.',
        read_only=True,
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
        allow_mutation=False,
        description='The **name** for the User_Group.',
        read_only=True,
        title='name',
    )
    users: 'UsersModel' = Field(
        None,
        allow_mutation=False,
        description='The **users** for the User_Group.',
        read_only=True,
        title='users',
    )

    @validator('users', always=True, pre=True)
    def _validate_users(cls, v):
        if not v:
            return UsersModel()  # type: ignore
        return v


class UserGroupDataModel(
    BaseModel,
    title='UserGroup Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """User_Groups Data Model"""

    data: list[UserGroupModel] | None = Field(
        [],
        description='The data for the UserGroups.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserGroupsModel(
    BaseModel,
    title='UserGroups Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """User_Groups Model"""

    _mode_support = PrivateAttr(False)

    data: list[UserGroupModel] | None = Field(
        [],
        description='The data for the UserGroups.',
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
from tcex.api.tc.v3.security.users.user_model import UsersModel

# add forward references
UserGroupDataModel.update_forward_refs()
UserGroupModel.update_forward_refs()
UserGroupsModel.update_forward_refs()
