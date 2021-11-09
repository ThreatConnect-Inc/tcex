"""User_Group / User_Groups Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

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
    """User_Groups Model"""

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
    """User_Groups Data Model"""

    data: Optional[List['UserGroupModel']] = Field(
        [],
        description='The data for the UserGroups.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserGroupModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='UserGroup Model',
    validate_assignment=True,
):
    """User_Group Model"""

    # slot attributes are not added to dict()/json()
    __slot__ = ('_privates_',)

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(**kwargs)
        super().__setattr__('_privates_', {'_modified_': 0})

    def __setattr__(self, name, value):
        """Update modified property on any update."""
        super().__setattr__('_privates_', {'_modified_': self.privates.get('_modified_', 0) + 1})
        super().__setattr__(name, value)

    @property
    def modified(self):
        """Return int value of modified (> 0 means modified)."""
        return self._privates_.get('_modified_', 0)

    @property
    def privates(self):
        """Return privates dict."""
        return self._privates_

    description: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description** for the User_Group.',
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
        description='The **name** for the User_Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
    users: Optional['UsersModel'] = Field(
        None,
        allow_mutation=False,
        description='The **users** for the User_Group.',
        read_only=True,
        title='users',
    )

    @validator('users', always=True)
    def _validate_users(cls, v):
        if not v:
            return UsersModel()
        return v


# first-party
from tcex.api.tc.v3.security.users.user_model import UsersModel

# add forward references
UserGroupDataModel.update_forward_refs()
UserGroupModel.update_forward_refs()
UserGroupsModel.update_forward_refs()
