"""System Role / System Roles Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class SystemRolesModel(
    BaseModel,
    title='SystemRoles Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """System Roles Model"""

    data: Optional[List['SystemRoleModel']] = Field(
        [],
        description='The data for the SystemRoles.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SystemRoleDataModel(
    BaseModel,
    title='SystemRole Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """System Roles Data Model"""

    data: Optional[List['SystemRoleModel']] = Field(
        [],
        description='The data for the SystemRoles.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SystemRoleModel(
    BaseModel,
    title='SystemRole Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """System Role Model"""

    active: bool = Field(
        None,
        allow_mutation=False,
        description='The **active** for the System Role.',
        read_only=True,
        title='active',
    )
    assignable: bool = Field(
        None,
        allow_mutation=False,
        description='The **assignable** for the System Role.',
        read_only=True,
        title='assignable',
    )
    displayed: bool = Field(
        None,
        allow_mutation=False,
        description='The **displayed** for the System Role.',
        read_only=True,
        title='displayed',
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
        description='The **name** for the System Role.',
        read_only=True,
        title='name',
    )


# add forward references
SystemRoleDataModel.update_forward_refs()
SystemRoleModel.update_forward_refs()
SystemRolesModel.update_forward_refs()
