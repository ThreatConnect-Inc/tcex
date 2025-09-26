"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class SystemRoleModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='SystemRole Model',
    validate_assignment=True,
):
    """System_Role Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    active: bool | None = Field(
        default=None,
        description='The **active** for the System_Role.',
        frozen=True,
        title='active',
        validate_default=True,
    )
    assignable: bool | None = Field(
        default=None,
        description='The **assignable** for the System_Role.',
        frozen=True,
        title='assignable',
        validate_default=True,
    )
    displayed: bool | None = Field(
        default=None,
        description='The **displayed** for the System_Role.',
        frozen=True,
        title='displayed',
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
        description='The **name** for the System_Role.',
        frozen=True,
        title='name',
        validate_default=True,
    )


class SystemRoleDataModel(
    BaseModel,
    title='SystemRole Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """System_Roles Data Model"""

    data: list[SystemRoleModel] | None = Field(
        [],
        description='The data for the SystemRoles.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class SystemRolesModel(
    BaseModel,
    title='SystemRoles Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """System_Roles Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[SystemRoleModel] | None = Field(
        [],
        description='The data for the SystemRoles.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
SystemRoleDataModel.model_rebuild()
SystemRoleModel.model_rebuild()
SystemRolesModel.model_rebuild()
