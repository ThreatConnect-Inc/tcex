"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class UserModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='User Model',
    validate_assignment=True,
):
    """User Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    user_name: str | None = Field(
        None,
        allow_mutation=False,
        description='The **user name** for the User.',
        read_only=True,
        title='userName',
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
        methods=['POST', 'PUT'],
        title='data',
    )


class UsersModel(
    BaseModel,
    title='Users Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Users Model"""

    _mode_support = PrivateAttr(False)

    data: list[UserModel] | None = Field(
        [],
        description='The data for the Users.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


# add forward references
UserDataModel.update_forward_refs()
UserModel.update_forward_refs()
UsersModel.update_forward_refs()
