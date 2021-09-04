"""System Role Model"""
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
        description='The data for the SystemRole.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SystemRoleData(
    BaseModel,
    title='SystemRole Data',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """System Role Data"""

    data: Optional['SystemRoleModel'] = Field(
        None,
        description='The data for the SystemRole.',
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
        description='The **active** for the SystemRole.',
        read_only=True,
        title='active',
    )
    assignable: bool = Field(
        None,
        allow_mutation=False,
        description='The **assignable** for the SystemRole.',
        read_only=True,
        title='assignable',
    )
    displayed: bool = Field(
        None,
        allow_mutation=False,
        description='The **displayed** for the SystemRole.',
        read_only=True,
        title='displayed',
    )
    id: Optional[int] = Field(
        None,
        description='The id of the **Object**.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **name** for the SystemRole.',
        read_only=True,
        title='name',
    )


# add forward references
SystemRoleData.update_forward_refs()
SystemRoleModel.update_forward_refs()
SystemRolesModel.update_forward_refs()
