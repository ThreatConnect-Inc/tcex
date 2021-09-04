"""Adversary Asset / Adversary Assets Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class AdversaryAssetsModel(
    BaseModel,
    title='AdversaryAssets Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Adversary Assets Model"""

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
    """Adversary Assets Data Model"""

    data: Optional[List['AdversaryAssetModel']] = Field(
        [],
        description='The data for the AdversaryAssets.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AdversaryAssetModel(
    BaseModel,
    title='AdversaryAsset Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Adversary Asset Model"""

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
AdversaryAssetDataModel.update_forward_refs()
AdversaryAssetModel.update_forward_refs()
AdversaryAssetsModel.update_forward_refs()
