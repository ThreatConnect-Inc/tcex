"""Case Management"""
# third-party
from requests import Session

# first-party
from tcex.api.v3.threat_intelligence.threat_intelligence import ThreatIntelligence


class V3:
    """Case Management

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session) -> None:
        """Initialize Class properties."""
        self.session = session

    @property
    def ti(self) -> ThreatIntelligence:
        """Return a instance of Adversary object."""
        return ThreatIntelligence(self.session)
