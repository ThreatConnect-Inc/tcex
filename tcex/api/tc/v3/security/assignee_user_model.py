"""ThreatConnect Assignee Module"""
# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import Field

# first-party
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.utils import Utils


class AssigneeUserModel(
    UserModel,
    title='Assignee User Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Assignee Model"""

    user_name: str | None = Field(
        None,
        allow_mutation=False,
        description='The **user name** for the User.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='userName',
    )
