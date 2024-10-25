"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.tcex_ti_tc_request import TiTcRequest

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class Tags:
    """Unique API calls for Tags API Endpoints"""

    def __init__(self, ti: 'ThreatIntelligence'):
        """Initialize instance properties."""

        # properties
        self._api_entity = 'tag'
        self._api_sub_type = None
        self._api_type = None
        self._tc_requests = TiTcRequest(ti.session_tc)
        self._type = 'tags'
        self.ti = ti

    def many(self, filters=None, owners=None, params=None):
        """Get all the tags."""
        for tag in self.tc_requests.all_tags(filters=filters, owners=owners, params=params):
            yield self.ti.tag(name=tag.get('name'))

    @property
    def tc_requests(self):
        """Get the tc request object"""
        return self._tc_requests

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """Set the tc request object."""
        self._tc_requests = tc_requests
