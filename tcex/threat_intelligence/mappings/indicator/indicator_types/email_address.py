# -*- coding: utf-8 -*-
"""ThreatConnect TI Email Address"""
from ..indicator import Indicator


class EmailAddress(Indicator):
    """Unique API calls for Email Address API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties.

        Args:
            address (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__(
            tcex,
            sub_type='Email Address',
            api_entity='emailAddress',
            api_branch='emailAddresses',
            **kwargs
        )
        self.unique_id = kwargs.get('unique_id', kwargs.get('address'))
        self._data['address'] = self.unique_id

    def can_create(self):
        """Return True if email address can be created.

        If the address has been provided returns that the EmailAddress can be created, otherwise
        returns that the EmailAddress cannot be created.

        Returns:

        """
        return not self.data.get('address') is None

    def _set_unique_id(self, json_response):
        """Set the unique_id provided a json response.

        Args:
            json_response:
        """
        self.unique_id = json_response.get('address', '')
