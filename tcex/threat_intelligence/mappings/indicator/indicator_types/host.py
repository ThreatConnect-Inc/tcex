# -*- coding: utf-8 -*-
"""ThreatConnect TI Host"""
# standard library
from urllib.parse import quote_plus

from ..indicator import Indicator


class Host(Indicator):
    """Unique API calls for Host API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties.

        Args:
            hostname (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            last_modified (str, kwargs): [Read-Only] The date timestamp the Indicator was last
                modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
            whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
        """
        super().__init__(tcex, sub_type='Host', api_entity='host', api_branch='hosts', **kwargs)
        self.unique_id = kwargs.get('unique_id', self._data.get('hostName'))
        self._data['hostName'] = self.unique_id
        if self.unique_id:
            self.unique_id = quote_plus(self.fully_decode_uri(self.unique_id))

    def can_create(self):
        """Return True if file can be create.

        If the hostName has been provided returns that the File can be created, otherwise
        returns that the Host cannot be created.
        """
        return not self.data.get('hostName') is None

    def _set_unique_id(self, json_response):
        """Set the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = quote_plus(self.fully_decode_uri(json_response.get('hostName', '')))

    def dns_resolution(self):
        """Update the Host DNS resolution

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.dns_resolution(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )

    def set_dns_resolution(self, value):
        """Update the Host DNS resolution

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        return self.tc_requests.set_dns_resolution(
            self.api_type, self.api_branch, self.unique_id, value, owner=self.owner
        )

    def set_whois(self, value):
        """Update the Indicators WhoIs

        Args:
            value:
        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.set_whois(
            self.api_type, self.api_branch, self.unique_id, value, owner=self.owner
        )
