"""Victim Asset / Victim Assets Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class VictimAssetsModel(
    BaseModel,
    title='VictimAssets Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Victim Assets Model"""

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
    """Victim Assets Data Model"""

    data: Optional[List['VictimAssetModel']] = Field(
        [],
        description='The data for the VictimAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class VictimAssetModel(
    BaseModel,
    title='VictimAsset Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Victim Asset Model"""

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


# add forward references
VictimAssetDataModel.update_forward_refs()
VictimAssetModel.update_forward_refs()
VictimAssetsModel.update_forward_refs()
