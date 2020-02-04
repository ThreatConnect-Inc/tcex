# -*- coding: utf-8 -*-
"""ThreatConnect TI Address"""
from ..indicator import Indicator


class Address(Indicator):
    """Unique API calls for Address API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties.

        Args:
            ip (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            last_modified (str, kwargs): [Read-Only] The date timestamp the Indicator was last
                modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
        """
        super().__init__(
            tcex, sub_type='Address', api_entity='address', api_branch='addresses', **kwargs
        )
        self.unique_id = kwargs.get('unique_id', kwargs.get('ip'))
        self.data['ip'] = self.unique_id

    def _set_unique_id(self, json_response):
        """Set the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('ip', '')

    def can_create(self):
        """Return True if address can be created.

        If the ip address has been provided returns that the address can be created, otherwise
        returns that the address cannot be created.
        """
        return not self.data.get('ip') is None

    # TODO: @burdy - is this correct for address?
    def dns_resolution(self):
        """Update the DNS resolution.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])
        return self.tc_requests.dns_resolution(
            self.api_type, self.api_branch, self.unique_id, owner=self.owner
        )
