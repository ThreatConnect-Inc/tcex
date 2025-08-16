"""TcEx Framework Module"""

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
        frozen=True,
        description='The **name** for the User_Group.',
        # TODO: @bsummers-tc
        # read_only=False,
        title='name',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )
