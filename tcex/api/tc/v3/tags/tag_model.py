"""Tag / Tags Model"""
# pylint: disable=no-member,no-self-argument,no-self-use,wrong-import-position
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr, validator

# first-party
from tcex.api.tc.v3.v3_model_abc import V3ModelABC
from tcex.utils import Utils


class TagsModel(
    BaseModel,
    title='Tags Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Tags Model"""

    _mode_support = PrivateAttr(True)

    data: Optional[List['TagModel']] = Field(
        [],
        description='The data for the Tags.',
        methods=['POST', 'PUT'],
        title='data',
    )
    mode: str = Field(
        'append',
        description='The PUT mode for nested objects (append, delete, replace). Default: append',
        methods=['POST', 'PUT'],
        title='append',
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
    V3ModelABC,
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    title='Tag Model',
    validate_assignment=True,
):
    """Tag Model"""

    _associated_type = PrivateAttr(False)
    _cm_type = PrivateAttr(False)
    _shared_type = PrivateAttr(True)
    _staged = PrivateAttr(False)

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
    groups: Optional['GroupsModel'] = Field(
        None,
        allow_mutation=False,
        description='The **groups** for the Tag.',
        read_only=True,
        title='groups',
    )
    id: Optional[int] = Field(
        None,
        description='The ID of the item.',
        read_only=True,
        title='id',
    )
    indicators: Optional['IndicatorsModel'] = Field(
        None,
        allow_mutation=False,
        description='The **indicators** for the Tag.',
        read_only=True,
        title='indicators',
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

    @validator('groups', always=True)
    def _validate_groups(cls, v):
        if not v:
            return GroupsModel()
        return v

    @validator('indicators', always=True)
    def _validate_indicators(cls, v):
        if not v:
            return IndicatorsModel()
        return v

    @validator('victims', always=True)
    def _validate_victims(cls, v):
        if not v:
            return VictimsModel()
        return v


# first-party
from tcex.api.tc.v3.cases.case_model import CasesModel
from tcex.api.tc.v3.groups.group_model import GroupsModel
from tcex.api.tc.v3.indicators.indicator_model import IndicatorsModel
from tcex.api.tc.v3.victims.victim_model import VictimsModel

# add forward references
TagDataModel.update_forward_refs()
TagModel.update_forward_refs()
TagsModel.update_forward_refs()
