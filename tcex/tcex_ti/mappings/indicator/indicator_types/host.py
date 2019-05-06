# -*- coding: utf-8 -*-
"""ThreatConnect TI Host"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator

try:
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote_plus  # Python


class Host(Indicator):
    """Unique API calls for Host API Endpoints"""

    def __init__(self, tcex, hostname, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            hostname (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
            whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
        """
        super(Host, self).__init__(tcex, 'Host', 'host', 'hosts', owner, **kwargs)
        self._data['hostName'] = hostname
        self.unique_id = self.unique_id or hostname
        if self.unique_id:
            self.unique_id = quote_plus(self.unique_id)

    def can_create(self):
        """
        If the hostName has been provided returns that the File can be created, otherwise
        returns that the Host cannot be created.

        Returns:

        """
        if self.data.get('hostName'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('hostName', '')

    def dns_resolution(self):
        """
        Updates the Host DNS resolution

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.dns_resolution(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )
