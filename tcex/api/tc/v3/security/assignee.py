"""ThreatConnect Assignee Module"""
# standard library
from typing import Union, Optional

# first-party
from tcex.utils import Utils
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel

# third-party
from pydantic import BaseModel, validator, Field


class AssigneeModel(
    BaseModel,
    title='User Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Users Data Model"""

    type: Optional[str] = Field(
        None,
        description='The **Type** for the Assignee.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='type',
    )

    data: Optional[Union[UserModel, UserGroupModel]] = Field(
        None,
        description='The **Data** for the Assignee.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='data',
    )

    @validator('type', always=True)
    def _validate_type(cls, v):
        if not v:
            return v
        if v.lower() == 'user':
            return 'User'
        elif v.lower() in ['group', 'user_group', 'usergroup']:
            return 'Group'

        raise ValueError('Value must be either `User` or `Group`.')
