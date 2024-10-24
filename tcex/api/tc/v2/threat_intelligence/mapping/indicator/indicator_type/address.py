"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator import Indicator

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class Address(Indicator):
    """Unique API calls for Address API Endpoints"""

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties.

        Args:
            ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
            ip (str): The value for this Indicator.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            last_modified (str, kwargs): [Read-Only] The date timestamp the Indicator was last
                modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
        """
        super().__init__(
            ti, sub_type='Address', api_entity='address', api_branch='addresses', **kwargs
        )
        self.unique_id = kwargs.get('unique_id', kwargs.get('ip'))
        self.data['ip'] = self.unique_id

    def _set_unique_id(self, json_response):
        """Set the unique_id provided a json response."""
        self.unique_id = json_response.get('ip', '')

    def can_create(self):
        """Return True if address can be created.

        If the ip address has been provided returns that the address can be created, otherwise
        returns that the address cannot be created.
        """
        return self.data.get('ip') is not None

    def dns_resolution(self):
        """Update the DNS resolution."""
        if not self.can_update():
            self._handle_error(910, [self.type])
        return self.tc_requests.dns_resolution(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )
