"""ThreatConnect Assignee Module"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import Optional, Union

# third-party
from pydantic import Field, validator

# first-party
from tcex.api.tc.v3.security.assignee_user_group_model import AssigneeUserGroupModel
from tcex.api.tc.v3.security.assignee_user_model import AssigneeUserModel
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class AssigneeModel(
    V3ModelABC,
    title='User Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Assignee Model"""

    type: Optional[str] = Field(
        None,
        description='The **Type** for the Assignee.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='type',
    )

    data: Optional[Union[AssigneeUserModel, AssigneeUserGroupModel]] = Field(
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

        if v.lower() in ['group', 'user_group', 'usergroup']:
            return 'Group'

        raise ValueError('Value must be either `User` or `Group`.')
