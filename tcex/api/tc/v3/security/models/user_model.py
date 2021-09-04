"""User Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

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
        description='The data for the User.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserData(
    BaseModel,
    title='User Data',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """User Data"""

    data: Optional['UserModel'] = Field(
        None,
        description='The data for the User.',
        methods=['POST', 'PUT'],
        title='data',
    )


class UserModel(
    BaseModel,
    title='User Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """User Model"""

    first_name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **first name** for the User.',
        read_only=True,
        title='firstName',
    )
    id: Optional[int] = Field(
        None,
        description='The id of the **Object**.',
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
UserData.update_forward_refs()
UserModel.update_forward_refs()
UsersModel.update_forward_refs()
