# -*- coding: utf-8 -*-
"""ThreatConnect TI Address"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class Address(Indicator):
    """Unique API calls for Address API Endpoints"""

    def __init__(self, tcex, ip, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            ip (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
        """
        super(Address, self).__init__(tcex, 'Address', 'address', 'addresses', owner, **kwargs)
        self.data['ip'] = ip
        self.unique_id = self.unique_id or ip

    def can_create(self):
        """
        If the ip address has been provided returns that the address can be created, otherwise
        returns that the address cannot be created.

        Returns:

        """
        if self.data.get('ip'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('ip', '')

    def dns_resolution(self):
        """
        Updates the DNS resolution.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.dns_resolution(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )
