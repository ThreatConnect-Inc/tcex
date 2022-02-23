"""Victim / Victims Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class VictimsModel(
    BaseModel,
    title='Victims Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Victims Model"""

    _mode_support = PrivateAttr(False)

    data: Optional[List['VictimModel']] = Field(
        [],
        description='The data for the Victims.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
    )


class VictimDataModel(
    BaseModel,
    title='Victim Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Victims Data Model"""

    data: Optional[List['VictimModel']] = Field(
        [],
        description='The data for the Victims.',
        methods=['POST', 'PUT'],
        title='data',
    )


class VictimModel(
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Victim Model',
    validate_assignment=True,
):
    """Victim Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(False)
    _staged = PrivateAttr(False)

    assets: Optional['VictimAssetsModel'] = Field(
        None,
        description='A list of victim assets corresponding to the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='assets',
    )
    associated_groups: Optional['GroupsModel'] = Field(
        None,
        description='A list of groups that this victim is associated with.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='associatedGroups',
    )
    attributes: Optional['VictimAttributesModel'] = Field(
        None,
        description='A list of Attributes corresponding to the Victim.',
        methods=['POST', 'PUT'],
        read_only=False,
        title='attributes',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the item was first created.',
        read_only=True,
        title='dateAdded',
    )
    description: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='Description of the Victim.',
        max_length=255,
        min_length=0,
        read_only=True,
        title='description',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    name: Optional[str] = Field(
        None,
        description='Name of the Victim.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=1,
        read_only=False,
        title='name',
    )
    nationality: Optional[str] = Field(
        None,
        description='Nationality of the Victim.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=0,
        read_only=False,
        title='nationality',
    )
    org: Optional[str] = Field(
        None,
        description='Org of the Victim.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=0,
        read_only=False,
        title='org',
    )
    owner_name: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='The name of the Organization, Community, or Source that the item belongs to.',
        read_only=True,
        title='ownerName',
    )
    security_labels: Optional['SecurityLabelsModel'] = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='securityLabels',
    )
    suborg: Optional[str] = Field(
        None,
        description='Suborg of the Victim.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=0,
        read_only=False,
        title='suborg',
    )
    tags: Optional['TagsModel'] = Field(
        None,
        description=(
            'A list of Tags corresponding to the item (NOTE: Setting this parameter will replace '
            'any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        read_only=False,
        title='tags',
    )
    web_link: Optional[str] = Field(
        None,
        allow_mutation=False,
        description='A link to the ThreatConnect details page for this entity.',
        read_only=True,
        title='webLink',
    )
    work_location: Optional[str] = Field(
        None,
        description='Work location of the Victim.',
        methods=['POST', 'PUT'],
        max_length=100,
        min_length=0,
        read_only=False,
        title='workLocation',
    )

    @validator('associated_groups', always=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()
        return v

    @validator('security_labels', always=True)
    def _validate_security_labels(cls, v):
        if not v:
            return SecurityLabelsModel()
        return v

    @validator('tags', always=True)
    def _validate_tags(cls, v):
        if not v:
            return TagsModel()
        return v

    @validator('assets', always=True)
    def _validate_victim_assets(cls, v):
        if not v:
            return VictimAssetsModel()
        return v

    @validator('attributes', always=True)
    def _validate_victim_attributes(cls, v):
        if not v:
            return VictimAttributesModel()
        return v


# first-party
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.security_labels.security_label_model import SecurityLabelsModel
from tcex.api.tc.v3.tags.tag_model import TagsModel
from tcex.api.tc.v3.victim_assets.victim_asset_model import VictimAssetsModel
from tcex.api.tc.v3.victim_attributes.victim_attribute_model import VictimAttributesModel

# add forward references
VictimDataModel.update_forward_refs()
VictimModel.update_forward_refs()
VictimsModel.update_forward_refs()
