"""Attribute Model"""
# standard library
from datetime import datetime
from typing import List, Optional

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class AttributesModel(
    BaseModel,
    title='Attributes Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Attributes Model"""

    data: Optional[List['AttributeModel']] = Field(
        [],
        description='The data for the Attribute.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AttributeData(
    BaseModel,
    title='Attribute Data',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True,
):
    """Attribute Data"""

    data: Optional['AttributeModel'] = Field(
        None,
        description='The data for the Attribute.',
        methods=['POST', 'PUT'],
        title='data',
    )


class AttributeModel(
    BaseModel,
    title='Attribute Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True,
):
    """Attribute Model"""

    date_added: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was added.',
        read_only=True,
        title='dateAdded',
    )
    id: int = Field(
        None,
        allow_mutation=False,
        description='The **attribute** Id.',
        read_only=True,
        title='id',
    )
    last_modified: Optional[datetime] = Field(
        None,
        allow_mutation=False,
        description='The date and time that the Attribute was last modified.',
        read_only=True,
        title='lastUsed',
    )
    type: str = Field(
        None,
        description='The defined attribute type.',
        methods=['POST', 'PUT'],
        max_length=255,
        min_length=0,
        read_only=False,
        title='type',
    )
    value: Optional[str] = Field(
        None,
        description='The attribute value.',
        methods=['POST', 'PUT'],
        read_only=True,
        title='value',
    )


# add forward references
AttributeData.update_forward_refs()
AttributeModel.update_forward_refs()
AttributesModel.update_forward_refs()
