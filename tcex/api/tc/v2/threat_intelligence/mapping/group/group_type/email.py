"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class Email(Group):
    """Unique API calls for Email API Endpoints

    Args:
        ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
        body (str): The body for this Email.
        from_addr (str, kwargs): The **from** address for this Email.
        header (str): The header for this Email.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
        subject (str): The subject for this Email.
        to (str, kwargs): The **to** address for this Email.
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties."""
        super().__init__(ti, sub_type='Email', api_entity='email', api_branch='emails', **kwargs)
