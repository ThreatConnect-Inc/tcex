"""TcEx Framework Module"""

# first-party
from tcex.api.tc.v3.attribute_types.attribute_type import AttributeType, AttributeTypes
from tcex.api.tc.v3.case_management.case_management import CaseManagement
from tcex.api.tc.v3.intel_requirement.ir import IR
from tcex.api.tc.v3.security.security import Security
from tcex.api.tc.v3.threat_intelligence.threat_intelligence import ThreatIntelligence
from tcex.pleb.cached_property import cached_property


class V3(CaseManagement, Security, ThreatIntelligence, IR):
    """V3 API Collection

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def attribute_type(self, **kwargs) -> AttributeType:
        """Return a instance of Attribute Types object."""
        return AttributeType(session=self.session, **kwargs)

    def attribute_types(self, **kwargs) -> AttributeTypes:
        """Return a instance of Attribute Types object."""
        return AttributeTypes(session=self.session, **kwargs)

    @cached_property
    def cm(self) -> CaseManagement:
        """Return Case Management API collection."""
        return CaseManagement(self.session)

    @cached_property
    def ir(self) -> IR:
        """Return Intel Requirement API collection."""
        return IR(self.session)

    @cached_property
    def security(self) -> Security:
        """Return Security API collection."""
        return Security(self.session)

    @cached_property
    def ti(self) -> ThreatIntelligence:
        """Return Threat Intelligence API collection."""
        return ThreatIntelligence(self.session)
