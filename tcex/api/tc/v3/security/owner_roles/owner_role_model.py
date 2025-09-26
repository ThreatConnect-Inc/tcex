"""TcEx Framework Module"""

from __future__ import annotations

from pydantic import BaseModel, Field, PrivateAttr

from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class OwnerRoleModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra='allow',
    title='OwnerRole Model',
    validate_assignment=True,
):
    """Owner_Role Model"""

    _associated_type: bool = PrivateAttr(default=False)
    _cm_type: bool = PrivateAttr(default=False)
    _shared_type: bool = PrivateAttr(default=False)
    _staged: bool = PrivateAttr(default=False)

    available: bool | None = Field(
        default=None,
        description='The **available** for the Owner_Role.',
        frozen=True,
        title='available',
        validate_default=True,
    )
    comm_role: bool | None = Field(
        default=None,
        description='The **comm role** for the Owner_Role.',
        frozen=True,
        title='commRole',
        validate_default=True,
    )
    description_admin: str | None = Field(
        default=None,
        description='The **description admin** for the Owner_Role.',
        frozen=True,
        title='descriptionAdmin',
        validate_default=True,
    )
    description_comm: str | None = Field(
        default=None,
        description='The **description comm** for the Owner_Role.',
        frozen=True,
        title='descriptionComm',
        validate_default=True,
    )
    description_org: str | None = Field(
        default=None,
        description='The **description org** for the Owner_Role.',
        frozen=True,
        title='descriptionOrg',
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
        description='The **name** for the Owner_Role.',
        frozen=True,
        title='name',
        validate_default=True,
    )
    org_role: bool | None = Field(
        default=None,
        description='The **org role** for the Owner_Role.',
        frozen=True,
        title='orgRole',
        validate_default=True,
    )
    version: int | None = Field(
        default=None,
        description='The **version** for the Owner_Role.',
        frozen=True,
        title='version',
        validate_default=True,
    )


class OwnerRoleDataModel(
    BaseModel,
    title='OwnerRole Data Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Owner_Roles Data Model"""

    data: list[OwnerRoleModel] | None = Field(
        [],
        description='The data for the OwnerRoles.',
        title='data',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


class OwnerRolesModel(
    BaseModel,
    title='OwnerRoles Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Owner_Roles Model"""

    _mode_support: bool = PrivateAttr(default=False)

    data: list[OwnerRoleModel] | None = Field(
        [],
        description='The data for the OwnerRoles.',
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        title='append',
        json_schema_extra={'methods': ['POST', 'PUT']},
    )


# rebuild model
OwnerRoleDataModel.model_rebuild()
OwnerRoleModel.model_rebuild()
OwnerRolesModel.model_rebuild()
