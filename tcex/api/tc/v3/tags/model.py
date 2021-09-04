"""Tag / Tags Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field, validator

# first-party
from tcex.utils import Utils

class TagsModel(
    BaseModel,
    title='Tags Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Tags Model"""

    data: Optional[List['TagModel']] = Field(
        [],
        description='The data for the Tags.',
        methods=['POST', 'PUT'],
        title='data',
    )


class TagDataModel(
    BaseModel,
    title='Tag Data Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Tags Data Model"""

    data: Optional[List['TagModel']] = Field(
        [],
        description='The data for the Tags.',
        methods=['POST', 'PUT'],
        title='data',
    )


class TagModel(
    BaseModel,
    title='Tag Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Tag Model"""

    cases: Optional['CasesModel'] = Field(
        None,
        allow_mutation=False,
        description='The **cases** for the Tag.',
        read_only=True,
        title='cases',
    )
    description: Optional[str] = Field(
        None,
        description='A brief description of the Tag.',
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
    last_used: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Tag was last used.',
        read_only=True,
        title='lastUsed',
    )
    name: Optional[str] = Field(
        None,
        description='The **name** for the Tag.',
        methods=['POST', 'PUT'],
        max_length=128,
        min_length=1,
        read_only=False,
        title='name',
    )
    owner: Optional[str] = Field(
        None,
        description='The name of the Owner of the Tag.',
        methods=['POST'],
        read_only=False,
        title='owner',
        updatable=False,
    )
    victims: Optional['VictimsModel'] = Field(
        None,
        allow_mutation=False,
        description='The **victims** for the Tag.',
        read_only=True,
        title='victims',
    )

    @validator('cases', always=True)
    def _validate_cases(cls, v):
        if not v:
            return CasesModel()
        return v

    @validator('victims', always=True)
    def _validate_victims(cls, v):
        if not v:
            return VictimsModel()
        return v


# first-party
from tcex.api.tc.v3.cases.model import CasesModel
from tcex.api.tc.v3.victims.model import VictimsModel

# add forward references
TagDataModel.update_forward_refs()
TagModel.update_forward_refs()
TagsModel.update_forward_refs()
