"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import Field

# first-party
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.util import Util


class AssigneeUserGroupModel(
    UserGroupModel,
    title='Assignee User Group Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Assignee Model"""

    name: str | None = Field(
        None,
        allow_mutation=False,
        description='The **name** for the User_Group.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='name',
    )
