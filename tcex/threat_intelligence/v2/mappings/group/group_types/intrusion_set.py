"""ThreatConnect TI Intrusion Set"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.threat_intelligence.v2.mappings.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.threat_intelligence.v2 import ThreatIntelligence


class IntrusionSet(Group):
    """Unique API calls for IntrustionSet API Endpoints

    Args:
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize Class Properties."""
        super().__init__(
            ti,
            sub_type='Intrusion Set',
            api_entity='intrusionSet',
            api_branch='intrusionSets',
            **kwargs
        )
