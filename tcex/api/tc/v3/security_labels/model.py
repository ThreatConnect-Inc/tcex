"""Security Label / Security Labels Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class SecurityLabelsModel(
    BaseModel,
    title='SecurityLabels Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Security Labels Model"""

    data: Optional[List['SecurityLabelModel']] = Field(
        [],
        description='The data for the SecurityLabels.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SecurityLabelDataModel(
    BaseModel,
    title='SecurityLabel Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Security Labels Data Model"""

    data: Optional[List['SecurityLabelModel']] = Field(
        [],
        description='The data for the SecurityLabels.',
        methods=['POST', 'PUT'],
        title='data',
    )


class SecurityLabelModel(
    BaseModel,
    title='SecurityLabel Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Security Label Model"""

    attributes: AttributeDatas = Field(
        None,
        allow_mutation=False,
        description='Victim attributes associated with the security label.',
        read_only=True,
        title='attributes',
    )
    color: Optional[str] = Field(
        None,
        description='Color of the security label.',
        methods=['POST', 'PUT'],
        max_length=10,
        min_length=1,
        read_only=False,
        title='color',
    )
    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the label was added.',
        read_only=True,
        title='dateAdded',
    )
    description: Optional[str] = Field(
        None,
        description='Description of the security label.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=1,
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
        description='Name of the security label.',
        methods=['POST', 'PUT'],
        max_length=50,
        min_length=1,
        read_only=False,
        title='name',
    )
    owner: Optional[str] = Field(
        None,
        description='The name of the Owner of the Label.',
        methods=['POST'],
        read_only=False,
        title='owner',
        updatable=False,
    )
    victims: Optional['VictimsModel'] = Field(
        None,
        allow_mutation=False,
        description='Victims associated with the security label.',
        read_only=True,
        title='victims',
    )

    @validator('victims', always=True)
    def _validate_victims(cls, v):
        if not v:
            return VictimsModel()
        return v


# first-party
from tcex.api.tc.v3.victims.model import VictimsModel

# add forward references
SecurityLabelDataModel.update_forward_refs()
SecurityLabelModel.update_forward_refs()
SecurityLabelsModel.update_forward_refs()
