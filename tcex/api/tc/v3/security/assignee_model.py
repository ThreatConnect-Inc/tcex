"""TcEx Framework Module"""

# standard library

# third-party
from pydantic import Field, validator

# first-party
from tcex.api.tc.v3.security.assignee_user_group_model import AssigneeUserGroupModel
from tcex.api.tc.v3.security.assignee_user_model import AssigneeUserModel
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class AssigneeModel(
    V3ModelABC,
    title='User Data Model',
    alias_generator=Util().snake_to_camel,
    fields={'id': {'exclude': True}},
    validate_assignment=True,
):
    """Assignee Model"""

    type: str | None = Field(
        None,
        description='The **Type** for the Assignee.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='type',
    )

    data: AssigneeUserModel | AssigneeUserGroupModel | None = Field(
        None,
        description='The **Data** for the Assignee.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='data',
    )

    @validator('type', always=True)
    @classmethod
    def _validate_type(cls, v):
        if not v:
            return v

        if v.lower() == 'user':
            return 'User'

        if v.lower() in ['group', 'user_group', 'usergroup']:
            return 'Group'

        ex_msg = 'Value must be either `User` or `Group`.'
        raise ValueError(ex_msg)
