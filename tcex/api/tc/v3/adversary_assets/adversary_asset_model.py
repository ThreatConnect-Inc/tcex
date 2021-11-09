"""Adversary_Asset / Adversary_Assets Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

# json-encoder
json_encoders = {datetime: lambda v: v.isoformat()}


class AdversaryAssetsModel(
    BaseModel,
    title='AdversaryAssets Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Adversary_Assets Model"""

    data: Optional[List['AdversaryAssetModel']] = Field(
        [],
        description='The data for the AdversaryAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AdversaryAssetDataModel(
    BaseModel,
    title='AdversaryAsset Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Adversary_Assets Data Model"""

    data: Optional[List['AdversaryAssetModel']] = Field(
        [],
        description='The data for the AdversaryAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AdversaryAssetModel(
    BaseModel,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='AdversaryAsset Model',
    validate_assignment=True,
    json_encoders=json_encoders,
):
    """Adversary_Asset Model"""

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

    associated_groups: Optional['GroupsModel'] = Field(
        None,
        description='A list of groups that this victim asset is associated with.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        description='Name of victim asset.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
        read_only=False,
        title='name',
    )
    type: Optional[str] = Field(
        None,
        description='Type of victim asset.',
        methods=['POST'],
        min_length=1,
        read_only=False,
        title='type',
        updatable=False,
    )
    victim_id: Optional[int] = Field(
        None,
        description='Victim id of victim asset.',
        methods=['POST'],
        read_only=False,
        title='victimId',
        updatable=False,
    )

    @validator('associated_groups', always=True)
    def _validate_associated_groups(cls, v):
        if not v:
            return GroupsModel()
        return v


# first-party
from tcex.api.tc.v3.groups.group_model import GroupsModel

# add forward references
AdversaryAssetDataModel.update_forward_refs()
AdversaryAssetModel.update_forward_refs()
AdversaryAssetsModel.update_forward_refs()
