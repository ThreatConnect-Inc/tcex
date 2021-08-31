"""Artifact Model"""
# standard library
from typing import Optional, List

# third-party
from pydantic import BaseModel, Extra, Field

# first-party
from tcex.utils import Utils
from tcex.api.v3.threat_intelligence.model.threat_intelligence_abc import ThreatIntelligenceModel



class Indicators(
    BaseModel,
    title='Indicators Model',
):
    """Artifacts Model"""

    data: 'Optional[List[Indicator]]' = Field(
        [],
        description='The data for the File.',
        title='data',
    )


class Indicator(
    ThreatIntelligenceModel,
    title='Indicator Model',
    alias_generator=Utils().snake_to_camel,
    extra=Extra.allow,
    validate_assignment=True
):
    id: Optional[int] = Field(
        None,
        description='The **id** of the Indicator.',
        methods=['POST'],
        id='id',
    )


# add forward references
Indicator.update_forward_refs()
Indicators.update_forward_refs()
