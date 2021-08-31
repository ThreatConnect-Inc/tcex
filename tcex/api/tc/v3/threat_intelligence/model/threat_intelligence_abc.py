"""Artifact Model"""
# standard library
from typing import Optional

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils


class ThreatIntelligenceModel(
    BaseModel,
    title='Tag Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True
):
    attributes: Optional['Attributes'] = Field(
        None,
        description='The **name** of the Tag.',
        methods=['POST', 'PUT'],
        title='attributes'
    )

    tags: Optional['Tags'] = Field(
        None,
        description='The **name** of the Tag.',
        methods=['POST', 'PUT'],
        title='tags'
    )
    security_labels: Optional['SecurityLabels'] = Field(
        None,
        description='The **name** of the Tag.',
        methods=['POST', 'PUT'],
        title='securityLabels'
    )

    type: str = Field(
        None,
        description='The **type** of Threat Intelligence object.',
        methods=['POST', 'PUT'],
        title='type'
    )

    id: str = Field(
        None,
        description='The **id** of Threat Intelligence object.',
        methods=['PUT'],
        title='id'
    )


from tcex.api.v3.threat_intelligence.model.security_label import SecurityLabels
from tcex.api.v3.threat_intelligence.model.tag import Tags
from tcex.api.v3.threat_intelligence.model.attribute import Attributes

ThreatIntelligenceModel.update_forward_refs()
