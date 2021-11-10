"""ThreatConnect TI Security Label"""
# first-party
from tcex.utils import Utils

from ..tcex_ti_tc_request import TiTcRequest


class Tags:
    """Unique API calls for Tags API Endpoints"""

    def __init__(self, ti: 'ThreatIntelligenc'):
        """Initialize Class Properties."""

        # properties
        self._api_entity = 'tag'
        self._api_sub_type = None
        self._api_type = None
        self._tc_requests = TiTcRequest(ti.session)
        self._type = 'tags'
        self._utils = Utils()
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
        """Set the tc request object.

        Args:
            tc_requests:

        Returns:

        """
        self._tc_requests = tc_requests
