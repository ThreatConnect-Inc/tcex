"""Artifact Model"""
# standard library
from pydantic import Field

from typing import Optional

from tcex.api.v3.threat_intelligence.group.model.group_abc import Groups as GroupsModel
from tcex.api.v3.threat_intelligence.group.model.group_abc import Group as GroupModel


class Adversaries(
    GroupsModel,
    title='Adversaries Model',
):
    pass


class Adversary(
    GroupModel,
    title='Adversary Model',
):
    associated_indicators: Optional['All_Indicators'] = Field(
        None,
        description='The **associatedIndicators** of the group.',
        id='associatedIndicators'
    )
    associated_groups: Optional['All_Groups'] = Field(
        None,
        description='The **associatedGroups** of the group.',
        id='associatedGroups'
    )


from tcex.api.v3.threat_intelligence.indicator.model.all_indicators import All_Indicators
from tcex.api.v3.threat_intelligence.group.model.all_groups import All_Groups

Adversary.update_forward_refs()
Adversaries.update_forward_refs()
