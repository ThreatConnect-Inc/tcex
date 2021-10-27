"""User / Users Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class UsersModel(
    BaseModel,
    title='Users Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Users Model"""

    data: Optional[List['UserModel']] = Field(
        [],
        description='The data for the Users.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserDataModel(
    BaseModel,
    title='User Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Users Data Model"""

    data: Optional[List['UserModel']] = Field(
        [],
        description='The data for the Users.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='User Model',
    validate_assignment=True,
):
    """User Model"""

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

    first_name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **first name** for the User.',
        read_only=True,
        title='firstName',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    last_name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **last name** for the User.',
        read_only=True,
        title='lastName',
    )
    pseudonym: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **pseudonym** for the User.',
        read_only=True,
        title='pseudonym',
    )
    role: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **role** for the User.',
        read_only=True,
        title='role',
    )
    user_name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **user name** for the User.',
        read_only=True,
        title='userName',
    )


# add forward references
UserDataModel.update_forward_refs()
UserModel.update_forward_refs()
UsersModel.update_forward_refs()
