"""User Group / User Groups Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class UserGroupsModel(
    BaseModel,
    title='UserGroups Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """User Groups Model"""

    data: Optional[List['UserGroupModel']] = Field(
        [],
        description='The data for the UserGroups.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserGroupDataModel(
    BaseModel,
    title='UserGroup Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """User Groups Data Model"""

    data: Optional[List['UserGroupModel']] = Field(
        [],
        description='The data for the UserGroups.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserGroupModel(
    BaseModel,
    title='UserGroup Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """User Group Model"""

    description: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description** for the User Group.',
        read_only=True,
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
        allow_mutation=False,
        description='The **name** for the User Group.',
        read_only=True,
        title='name',
    )
    users: Optional['UsersModel'] = Field(
        None,
        allow_mutation=False,
        description='The **users** for the User Group.',
        read_only=True,
        title='users',
    )

    @validator('users', always=True)
    def _validate_users(cls, v):
        if not v:
            return UsersModel()
        return v


# first-party
from tcex.api.tc.v3.security.users.model import UsersModel

# add forward references
UserGroupDataModel.update_forward_refs()
UserGroupModel.update_forward_refs()
UserGroupsModel.update_forward_refs()
