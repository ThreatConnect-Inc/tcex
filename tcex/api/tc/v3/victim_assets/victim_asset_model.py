"""Victim_Asset / Victim_Assets Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils

# json-encoder
json_encoders = {datetime: lambda v: v.isoformat()}


class VictimAssetsModel(
    BaseModel,
    title='VictimAssets Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Victim_Assets Model"""

    data: Optional[List['VictimAssetModel']] = Field(
        [],
        description='The data for the VictimAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class VictimAssetDataModel(
    BaseModel,
    title='VictimAsset Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Victim_Assets Data Model"""

    data: Optional[List['VictimAssetModel']] = Field(
        [],
        description='The data for the VictimAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class VictimAssetModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='VictimAsset Model',
    validate_assignment=True,
    json_encoders=json_encoders,
):
    """Victim_Asset Model"""

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
VictimAssetDataModel.update_forward_refs()
VictimAssetModel.update_forward_refs()
VictimAssetsModel.update_forward_refs()
