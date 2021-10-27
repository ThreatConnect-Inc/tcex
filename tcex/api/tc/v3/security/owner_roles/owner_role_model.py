"""Owner_Role / Owner_Roles Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class OwnerRolesModel(
    BaseModel,
    title='OwnerRoles Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Owner_Roles Model"""

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
    """Owner_Roles Data Model"""

    data: Optional[List['OwnerRoleModel']] = Field(
        [],
        description='The data for the OwnerRoles.',
        methods=['POST', 'PUT'],
        title='data',
    )


class OwnerRoleModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='OwnerRole Model',
    validate_assignment=True,
):
    """Owner_Role Model"""

    # slot attributes are not added to dict()/json()
    __slot__ = ('_privates_',)

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(**kwargs)
        super().__setattr__('_privates_', {'_modified_': 0})

    def __setattr__(self, name, value):
        """Update modified property on any update."""
        super().__setattr__('_privates_', {'_modified_': self.privates.get('_modified_', 0) + 1})
        super().__setattr__(name, value)

    @property
    def modified(self):
        """Return int value of modified (> 0 means modified)."""
        return self._privates_.get('_modified_', 0)

    @property
    def privates(self):
        """Return privates dict."""
        return self._privates_

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
    description_admin: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description admin** for the Owner_Role.',
        read_only=True,
        title='descriptionAdmin',
    )
    description_comm: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description comm** for the Owner_Role.',
        read_only=True,
        title='descriptionComm',
    )
    description_org: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The **description org** for the Owner_Role.',
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
    version: Optional[int] = Field(
        None,
        allow_mutation=False,
        description='The **version** for the Owner_Role.',
        read_only=True,
        title='version',
    )


# add forward references
OwnerRoleDataModel.update_forward_refs()
OwnerRoleModel.update_forward_refs()
OwnerRolesModel.update_forward_refs()
