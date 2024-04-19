"""TcEx Framework Module"""

# pylint: disable=no-member,no-self-argument,wrong-import-position
# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.util import Util


class OwnerRoleModel(
    V3ModelABC,
    alias_generator=Util().snake_to_camel,
    extra=Extra.allow,
    title='OwnerRole Model',
    validate_assignment=True,
):
    """Owner_Role Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    available: bool = Field(
        None,
        allow_mutation=False,
        description='The **available** for the Owner_Role.',
        read_only=True,
        title='available',
    )
    comm_role: bool = Field(
        None,
        allow_mutation=False,
        description='The **comm role** for the Owner_Role.',
        read_only=True,
        title='commRole',
    )
    description_admin: str | None = Field(
        None,
        allow_mutation=False,
        description='The **description admin** for the Owner_Role.',
        read_only=True,
        title='descriptionAdmin',
    )
    description_comm: str | None = Field(
        None,
        allow_mutation=False,
        description='The **description comm** for the Owner_Role.',
        read_only=True,
        title='descriptionComm',
    )
    description_org: str | None = Field(
        None,
        allow_mutation=False,
        description='The **description org** for the Owner_Role.',
        read_only=True,
        title='descriptionOrg',
    )
    id: int | None = Field(  # type: ignore
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: str | None = Field(
        None,
        allow_mutation=False,
        description='The **name** for the Owner_Role.',
        read_only=True,
        title='name',
    )
    org_role: bool = Field(
        None,
        allow_mutation=False,
        description='The **org role** for the Owner_Role.',
        read_only=True,
        title='orgRole',
    )
    version: int | None = Field(
        None,
        allow_mutation=False,
        description='The **version** for the Owner_Role.',
        read_only=True,
        title='version',
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
        methods=['POST', 'PUT'],
        title='data',
    )


class OwnerRolesModel(
    BaseModel,
    title='OwnerRoles Model',
    alias_generator=Util().snake_to_camel,
    validate_assignment=True,
):
    """Owner_Roles Model"""

    _mode_support = PrivateAttr(False)

    data: list[OwnerRoleModel] | None = Field(
        [],
        description='The data for the OwnerRoles.',
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
OwnerRoleDataModel.update_forward_refs()
OwnerRoleModel.update_forward_refs()
OwnerRolesModel.update_forward_refs()
