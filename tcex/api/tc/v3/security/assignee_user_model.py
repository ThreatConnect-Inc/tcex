"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position

# third-party
from pydantic import Field

# first-party
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.util import Util


class AssigneeUserModel(
    UserModel,
    title='Assignee User Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Assignee Model"""

    user_name: str = Field(
        ...,
        allow_mutation=False,
        description='The **user name** for the User.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='userName',
    )
