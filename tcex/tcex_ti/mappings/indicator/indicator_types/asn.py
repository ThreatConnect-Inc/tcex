# -*- coding: utf-8 -*-
"""ThreatConnect TI ASN"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class ASN(Indicator):
    """Unique API calls for ASN API Endpoints"""

    def __init__(self, tcex, as_number, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            as_number (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
        """
        super(ASN, self).__init__(tcex, 'ASN', 'asn', 'asns', owner, **kwargs)
        self.unique_id = kwargs.get('unique_id', as_number)
        self._data['AS Number'] = as_number or self.unique_id

    def can_create(self):
        """
        If the as_number has been provided returns that the ASN can be created, otherwise
        returns that the ASN cannot be created.

        Returns:

        """
        if self.data.get('AS Number'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('AS Number', '')
