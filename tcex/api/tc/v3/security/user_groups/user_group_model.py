"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class UserGroupModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='UserGroup Model',
    validate_assignment=True,
):
    """User_Group Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    description: str | None = Field(
        default=None,
        description='The **description** for the User_Group.',
        frozen=True,
        title='description',
        validate_default=True,
    )
    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    name: str | None = Field(
        default=None,
        description='The **name** for the User_Group.',
        frozen=True,
        title='name',
        validate_default=True,
    )
    users: UsersModel | None = Field(
        default=None,
        description='The **users** for the User_Group.',
        frozen=True,
        title='users',
        validate_default=True,
    )

    @field_validator('users', mode='before')
    @classmethod
    def _validate_users(cls, v):
        if not v:
            return UsersModel()  # type: ignore
        return v


class UserGroupDataModel(
    BaseModel,
    title='UserGroup Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """User_Groups Data Model"""

    data: list[UserGroupModel] | None = Field(
        [],
        description='The data for the UserGroups.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class UserGroupsModel(
    BaseModel,
    title='UserGroups Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """User_Groups Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[UserGroupModel] | None = Field(
        [],
        description='The data for the UserGroups.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


from tcex.api.tc.v3.security.users.user_model import UsersModel

# rebuild model
UserGroupDataModel.model_rebuild()
UserGroupModel.model_rebuild()
UserGroupsModel.model_rebuild()
