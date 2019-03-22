# -*- coding: utf-8 -*-
"""ThreatConnect TI URL"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class URL(Indicator):
    """Unique API calls for URL API Endpoints"""

    def __init__(self, tcex, text, **kwargs):
        """Initialize Class Properties.

        Args:
            text (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(URL, self).__init__(tcex, 'urls', **kwargs)
        self.api_entity = 'url'
        self.data['text'] = text

    def can_create(self):
        """
        Determines if the required data that the API endpoint is expecting is present.
        :return: Boolean
        """
        if self.data.get('text'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """

        :param json_response:
        """
        self.unique_id = json_response.get('text', '')
