"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.tcex_ti_tc_request import TiTcRequest

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class Owner:
    """Common API calls for for Indicators/SecurityLabels/Groups and Victims"""

    def __init__(self, ti: 'ThreatIntelligence'):
        """Initialize instance properties."""
        self._data = {}

        self._type = 'Owner'
        self._api_type = 'owners'
        self._api_entity = 'owner'

        self._tc_requests = TiTcRequest(ti.session_tc)

    @property
    def type(self):
        """Return main type."""
        return self._type

    @property
    def tc_requests(self):
        """Return tc request object."""
        return self._tc_requests

    @property
    def api_type(self):
        """Return api type."""
        return self._api_type

    @property
    def api_entity(self):
        """Return api entity."""
        return self._api_entity

    @api_entity.setter
    def api_entity(self, api_entity):
        """Set the Api Entity."""
        self._api_entity = api_entity

    @api_type.setter
    def api_type(self, api_type):
        """Set the Api Type."""
        self._api_type = api_type

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """Set the Tc Request Object."""
        self._tc_requests = tc_requests

    def single(self, unique_id):
        """Return main type."""
        return self.tc_requests.single(
            self.api_type,
            None,
            unique_id,
        )

    def many(self):
        """Get all of the owners available."""
        yield from self.tc_requests.many(self.api_type, None, self.api_entity)

    def mine(self):
        """Get all of my owners available."""
        return self.tc_requests.mine()

    def members(self):
        """Get all members for my owners."""
        yield from self.tc_requests.many(self.api_type, 'mine/members', 'user')

    def metrics(self):
        """Get all the metric for owners."""
        yield from self.tc_requests.many(self.api_type, 'metric', 'ownerMetric')
