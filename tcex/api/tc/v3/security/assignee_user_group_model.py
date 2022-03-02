"""ThreatConnect Assignee Module"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import Optional

# third-party
from pydantic import Field

# first-party
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.utils import Utils


class AssigneeUserGroupModel(
    UserGroupModel,
    title='Assignee User Group Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Assignee Model"""

    name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **name** for the User_Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
