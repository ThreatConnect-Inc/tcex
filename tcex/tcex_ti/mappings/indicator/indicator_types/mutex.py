# -*- coding: utf-8 -*-
"""ThreatConnect TI Mutex"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator

try:
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote_plus  # Python


class Mutex(Indicator):
    """Unique API calls for Mutex API Endpoints"""

    def __init__(self, tcex, mutex, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            mutex (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
        """
        super(Mutex, self).__init__(tcex, 'Mutex', 'mutex', 'mutexes', owner, **kwargs)
        self.data['Mutex'] = mutex
        self.unique_id = self.unique_id or mutex
        if self.unique_id:
            self.unique_id = quote_plus(self.unique_id)

    def can_create(self):
        """
         If the mutex has been provided returns that the Mutex can be created, otherwise
         returns that the Mutex cannot be created.

         Returns:

         """
        if self.data.get('Mutex'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('Mutex', '')
