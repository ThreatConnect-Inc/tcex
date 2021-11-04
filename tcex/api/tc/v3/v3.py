"""V3 API"""

# first-party
from tcex.api.tc.v3.case_management.case_management import CaseManagement
from tcex.api.tc.v3.threat_intelligence.threat_intelligence import ThreatIntelligence


class V3(CaseManagement, ThreatIntelligence):
    """Case Management

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    @property
    def cm(self):
        """Return Case Management API collection."""
        return CaseManagement(self.session)

    @property
    def ti(self):
        """Return Threat Intelligence API collection."""
        return ThreatIntelligence(self.session)
