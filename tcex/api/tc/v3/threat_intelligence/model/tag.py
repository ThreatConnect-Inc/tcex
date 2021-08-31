"""Artifact Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class Tags(
    BaseModel,
    title='Tags Model',
):
    """Artifacts Model"""

    data: Optional[List['Tag']] = Field(
        [],
        description='The data for the Tag.',
        title='data',
    )


class Tag(
    BaseModel,
    title='Tag Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True
):
    name: str = Field(
        None,
        description='The **name** of the Tag.',
        methods=['POST', 'PUT'],
        title='name'
    )
    last_used: Optional[datetime] = Field(
        None,
        description='The **lastUsed** of the Tag.',
        title='lastUsed'
    )
    description: Optional[str] = Field(
        None,
        description='The **description** of the Tag.',
        title='description'
    )
    id: str = Field(
        None,
        description='The **id** of the Tag.',
        title='id'
    )

Tags.update_forward_refs()
Tag.update_forward_refs()
