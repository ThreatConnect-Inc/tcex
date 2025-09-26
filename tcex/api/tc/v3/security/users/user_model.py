"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class UserModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='User Model',
    validate_assignment=True,
):
    """User Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    id: int | None = Field(  # type: ignore
        default=None,
        description='The ID of the item.',
        title='id',
        validate_default=True,
    )
    user_name: str | None = Field(
        default=None,
        description='The **user name** for the User.',
        frozen=True,
        title='userName',
        validate_default=True,
    )


class UserDataModel(
    BaseModel,
    title='User Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Users Data Model"""

    data: list[UserModel] | None = Field(
        [],
        description='The data for the Users.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class UsersModel(
    BaseModel,
    title='Users Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Users Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[UserModel] | None = Field(
        [],
        description='The data for the Users.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
UserDataModel.model_rebuild()
UserModel.model_rebuild()
UsersModel.model_rebuild()
