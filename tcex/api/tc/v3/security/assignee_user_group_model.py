"""TcEx Framework Module"""

from pydantic import Field

from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.util import Util


class AssigneeUserGroupModel(
    UserGroupModel,
    title='Assignee User Group Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Assignee Model"""

    name: str | None = Field(  # type: ignore
        None,
        frozen=True,
        description='The **name** for the User_Group.',
        title='name',
        json_schema_extra={'methods': ['POST', 'PUT'], 'read_only': False},
    )
