"""Owner Role / Owner Roles Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class OwnerRolesModel(
    BaseModel,
    title='OwnerRoles Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Owner Roles Model"""

    data: Optional[List['OwnerRoleModel']] = Field(
        [],
        description='The data for the OwnerRoles.',
        methods=['POST', 'PUT'],
        title='data',
    )


class OwnerRoleDataModel(
    BaseModel,
    title='OwnerRole Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Owner Roles Data Model"""

    data: Optional[List['OwnerRoleModel']] = Field(
        [],
        description='The data for the OwnerRoles.',
        methods=['POST', 'PUT'],
        title='data',
    )


class OwnerRoleModel(
    BaseModel,
    title='OwnerRole Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Owner Role Model"""

    available: bool = Field(
        None,
        allow_mutation=False,
        description='The **available** for the Owner Role.',
        read_only=True,
        title='available',
    )
    comm_role: bool = Field(
        None,
        allow_mutation=False,
        description='The **comm role** for the Owner Role.',
        read_only=True,
        title='commRole',
    )
    description_admin: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description admin** for the Owner Role.',
        read_only=True,
        title='descriptionAdmin',
    )
    description_comm: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description comm** for the Owner Role.',
        read_only=True,
        title='descriptionComm',
    )
    description_org: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description org** for the Owner Role.',
        read_only=True,
        title='descriptionOrg',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **name** for the Owner Role.',
        read_only=True,
        title='name',
    )
    org_role: bool = Field(
        None,
        allow_mutation=False,
        description='The **org role** for the Owner Role.',
        read_only=True,
        title='orgRole',
    )
    version: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The **version** for the Owner Role.',
        read_only=True,
        title='version',
    )


# add forward references
OwnerRoleDataModel.update_forward_refs()
OwnerRoleModel.update_forward_refs()
OwnerRolesModel.update_forward_refs()
