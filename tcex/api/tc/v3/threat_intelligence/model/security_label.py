"""Artifact Model"""
# standard library
from datetime import datetime
from typing import Optional, List

# third-party
from pydantic import BaseModel, Field

# first-party
from tcex.utils import Utils


class SecurityLabels(
    BaseModel,
    title='Tags Model',
):
    """Artifacts Model"""

    data: Optional[List['SecurityLabel']] = Field(
        [],
        description='The data for the Tag.',
        title='data',
    )


class SecurityLabel(
    BaseModel,
    title='Tag Model',
    alias_generator=Utils().snake_to_camel,
    validate_assignment=True
):
    name: str = Field(
        None,
        description='The **name** of the Security Label.',
        methods=['POST', 'PUT'],
        title='name'
    )
    description: Optional[str] = Field(
        None,
        description='The **description** of the Security Label.',
        title='description'
    )
    date_added: Optional[datetime] = Field(
        None,
        description='The **dateAdded** of the Security Label.',
        title='dateAdded'
    )
    owner: Optional[str] = Field(
        None,
        description='The **owner** of the Security Label.',
        title='owner'
    )
    id: Optional[str] = Field(
        None,
        description='The **id** of the Security Label.',
        title='id'
    )
    color: Optional[str] = Field(
        None,
        description='The **color** of the Security Label.',
        title='color'
    )

SecurityLabels.update_forward_refs()
SecurityLabel.update_forward_refs()
