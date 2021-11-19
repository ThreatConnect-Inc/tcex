"""System_Role / System_Roles Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class SystemRolesModel(
    BaseModel,
    title='SystemRoles Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """System_Roles Model"""

    _mode_support = PrivateAttr(False)

    data: Optional[List['SystemRoleModel']] = Field(
        [],
        description='The data for the SystemRoles.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class SystemRoleDataModel(
    BaseModel,
    title='SystemRole Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """System_Roles Data Model"""

    data: Optional[List['SystemRoleModel']] = Field(
        [],
        description='The data for the SystemRoles.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SystemRoleModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='SystemRole Model',
    validate_assignment=True,
):
    """System_Role Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    active: bool = Field(
        None,
        allow_mutation=False,
        description='The **active** for the System_Role.',
        read_only=True,
        title='active',
    )
    assignable: bool = Field(
        None,
        allow_mutation=False,
        description='The **assignable** for the System_Role.',
        read_only=True,
        title='assignable',
    )
    displayed: bool = Field(
        None,
        allow_mutation=False,
        description='The **displayed** for the System_Role.',
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
        description='The **name** for the System_Role.',
        read_only=True,
        title='name',
    )


# add forward references
SystemRoleDataModel.update_forward_refs()
SystemRoleModel.update_forward_refs()
SystemRolesModel.update_forward_refs()
