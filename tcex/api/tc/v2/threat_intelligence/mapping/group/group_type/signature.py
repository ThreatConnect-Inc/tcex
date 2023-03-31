"""TcEx Framework Module"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class Signature(Group):
    """Unique API calls for Signature API Endpoints

    Valid file_types:
    + Snort
    + Suricata
    + YARA
    + ClamAV
    + OpenIOC
    + CybOX
    + Bro
    + Regex
    + SPL

    Args:
        ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
        file_name (str, kwargs): The name for the attached signature for this Group.
        file_type (str, kwargs): The signature type for this Group.
        file_text (str, kwargs): The signature content for this Group.
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties."""
        super().__init__(
            ti, sub_type='Signature', api_entity='signature', api_branch='signatures', **kwargs
        )

    def download(self):
        """Download the signature.

        Returns:
            obj: The Request response of the download request.
        """
        if not self.can_update():
            self._handle_error(910, [self.type])

        return self.tc_requests.download(self.api_type, self.api_branch, self.unique_id)
