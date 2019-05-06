# -*- coding: utf-8 -*-
"""ThreatConnect TI URL"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator

try:
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote_plus  # Python


class URL(Indicator):
    """Unique API calls for URL API Endpoints"""

    def __init__(self, tcex, text, owner=None, **kwargs):
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
        super(URL, self).__init__(tcex, 'URL', 'url', 'urls', owner, **kwargs)
        self.data['text'] = text
        self.unique_id = self.unique_id or text
        if self.unique_id:
            self.unique_id = quote_plus(self.unique_id)

    def can_create(self):
        """
         If the text has been provided returns that the URL can be created, otherwise
         returns that the URL cannot be created.

         Returns:

         """
        if self.data.get('text'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = quote_plus(json_response.get('text', ''))
