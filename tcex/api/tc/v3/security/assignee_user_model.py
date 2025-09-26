"""TcEx Framework Module"""

from pydantic import Field

from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.util import Util


class AssigneeUserModel(
    UserModel,
    title='Assignee User Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Assignee Model"""

    user_name: str = Field(  # type: ignore
        ...,
        frozen=True,
        description='The **user name** for the User.',
        # TODO: @bsummers-tc
        # read_only=False,
        title='userName',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
