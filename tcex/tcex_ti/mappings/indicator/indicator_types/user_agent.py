# -*- coding: utf-8 -*-
"""ThreatConnect TI User Agent"""
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class UserAgent(Indicator):
    """Unique API calls for UserAgent API Endpoints"""

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
        """
        super(UserAgent, self).__init__(
            tcex, 'User Agent', 'userAgent', 'userAgents', owner, **kwargs
        )
        self.unique_id = kwargs.get('unique_id', text)
        self.data['User Agent String'] = text or self.unique_id

    def can_create(self):
        """
         If the text has been provided returns that the UserAgent can be created, otherwise
         returns that the UserAgent cannot be created.

         Returns:

         """
        if self.data.get('User Agent String'):
            return True
        return False

    def _set_unique_id(self, json_response):
        """
        Sets the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('User Agent String', '')
