"""Artifact Model"""
# standard library
from pydantic import Field
from typing import Optional

from tcex.api.v3.threat_intelligence.indicator.model.indicator_abc import Indicators as IndicatorsModel
from tcex.api.v3.threat_intelligence.indicator.model.indicator_abc import Indicator as IndicatorModel



class Files(
    IndicatorsModel,
    title='Files Model',
):
    pass


class File(
    IndicatorModel,
    title='File Model',
):
    associated_groups: Optional['All_Groups'] = Field(
        None,
        description='The **associatedGroups** of the indicator.',
        id='associatedGroups'
    )


from tcex.api.v3.threat_intelligence.group.model.all_groups import All_Groups

File.update_forward_refs()
Files.update_forward_refs()
