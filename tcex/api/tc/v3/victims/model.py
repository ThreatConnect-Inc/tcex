"""Victim / Victims Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class VictimsModel(
    BaseModel,
    title='Victims Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Victims Model"""

    data: Optional[List['VictimModel']] = Field(
        [],
        description='The data for the Victims.',
        methods=['POST', 'PUT'],
        title='data',
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
    BaseModel,
    title='Victim Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Victim Model"""

    assets: Optional['VictimAssetsModel'] = Field(
        None,
        description='A list of victim assets corresponding to the Victim.',
        methods=['POST', 'PUT'],
        max_size=1000,
        read_only=False,
        title='assets',
    )
    attributes: Optional['AttributesModel'] = Field(
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
        description='Description of the Victim.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=0,
        read_only=False,
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
    security_labels: Optional['SecurityLabelsModel'] = Field(
        None,
        description=(
            'A list of Security Labels corresponding to the Intel item (NOTE: Setting this '
            'parameter will replace any existing tag(s) with the one(s) specified).'
        ),
        methods=['POST', 'PUT'],
        max_size=1000,
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
        max_size=1000,
        read_only=False,
        title='tags',
    )
    type: Optional[str] = Field(
        None,
        description='The **type** for the Victim.',
        methods=['POST', 'PUT'],
        min_length=1,
        read_only=False,
        title='type',
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

    @validator('attributes', always=True)
    def _validate_attributes(cls, v):
        if not v:
            return AttributesModel()
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
    def _validate_assets(cls, v):
        if not v:
            return VictimAssetsModel()
        return v


# first-party
from tcex.api.tc.v3.case_management.models.attribute_model import AttributesModel
from tcex.api.tc.v3.security_labels.model import SecurityLabelsModel
from tcex.api.tc.v3.tags.model import TagsModel
from tcex.api.tc.v3.victim_assets.model import VictimAssetsModel

# add forward references
VictimDataModel.update_forward_refs()
VictimModel.update_forward_refs()
VictimsModel.update_forward_refs()
