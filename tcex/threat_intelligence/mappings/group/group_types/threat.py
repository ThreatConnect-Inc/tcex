"""ThreatConnect TI Threat"""
from ..group import Group


class Threat(Group):
    """Unique API calls for Threat API Endpoints"""

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize Class Properties.

        Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
        """
        super().__init__(ti, sub_type='Threat', api_entity='threat', api_branch='threats', **kwargs)
