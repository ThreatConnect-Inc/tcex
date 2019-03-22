# -*- coding: utf-8 -*-
"""ThreatConnect TI ASN"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class ASN(Indicator):
    """Unique API calls for ASN API Endpoints"""

    def __init__(self, tcex, as_number, **kwargs):
        """Initialize Class Properties.

        Args:
            as_number (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(ASN, self).__init__(tcex, 'asns', **kwargs)
        self._api_entity = 'asn'
        self._data['as_number'] = as_number

    def can_create(self):
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get('as_number'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """

        :param json_response:
        """
        self.unique_id = json_response.get('as_number', '')
