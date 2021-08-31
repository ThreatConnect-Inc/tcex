"""Artifact Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.api.v3.threat_intelligence.model.threat_intelligence_abc import ThreatIntelligenceModel
from tcex.utils import Utils


class Groups(
    BaseModel,
    title='Groups Model',
):
    """Artifacts Model"""

    data: Optional[List['Group']] = Field(
        [],
        description='The data for the Group.',
        title='data',
    )


class Group(
    ThreatIntelligenceModel,
    title='Group Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True
):
    """Artifact Model"""

    type: Optional[str] = Field(
        None,
        description='The **type** of the Group.',
        methods=['POST'],
        title='type'
    )
    owner_name: Optional[str] = Field(
        None,
        description='The **ownerName** of the Group.',
        title='ownerName'
    )
    date_added: Optional[str] = Field(
        None,
        description='The **dateAdded** of the Group.',
        title='dateAdded'
    )
    web_link: Optional[str] = Field(
        None,
        description='The **webLink** of the Group.',
        title='webLink'
    )
    name: Optional[str] = Field(
        None,
        description='The **type** of the Group.',
        methods=['POST', 'PUT'],
        title='name'
    )
    created_by: Optional[str] = Field(
        None,
        description='The **createdBy** of the Group.',
        id='createdBy'
    )


# add forward references
Group.update_forward_refs()
Groups.update_forward_refs()
