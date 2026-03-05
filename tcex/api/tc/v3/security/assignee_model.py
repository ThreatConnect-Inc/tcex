"""TcEx Framework Module"""

from pydantic import ConfigDict, Field, field_validator

from tcex.api.tc.v3.security.assignee_user_group_model import AssigneeUserGroupModel
from tcex.api.tc.v3.security.assignee_user_model import AssigneeUserModel
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class AssigneeModel(V3ModelABC):
    """Assignee Model"""

    model_config = ConfigDict(
        title='User Data Model',
        alias_generator=Util().snake_to_camel,
        validate_assignment=True,
    )

    # Exclude inherited 'id' field
    id: int | None = Field(default=None, exclude=True)  # type: ignore

    type: str | None = Field(
        None,
        description='The **Type** for the Assignee.',
        # TODO: @bsummers-tc
        # read_only=False,
        title='type',
        validate_default=True,
        json_schema_extra={'methods': ['POST', 'PUT']},
    )

    data: AssigneeUserModel | AssigneeUserGroupModel | None = Field(
        None,
        description='The **Data** for the Assignee.',
        # TODO: @bsummers-tc
        # read_only=False,
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )

    @field_validator('data', mode='before')
    @classmethod
    def _validate_data(cls, v):
        if isinstance(v, UserModel) and not isinstance(v, AssigneeUserModel):
            return AssigneeUserModel.model_validate(v, from_attributes=True)
        if isinstance(v, UserGroupModel) and not isinstance(v, AssigneeUserGroupModel):
            return AssigneeUserGroupModel.model_validate(v, from_attributes=True)
        return v

    @field_validator('type')
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
