# -*- coding: utf-8 -*-
"""ThreatConnect TI Generic Mappings Object"""
# first-party
from tcex.utils import Utils

from ..tcex_ti_tc_request import TiTcRequest


class Owner:
    """Common API calls for for Indicators/SecurityLabels/Groups and Victims"""

    def __init__(self, tcex):
        """Initialize Class properties."""
        self._tcex = tcex
        self._data = {}

        self._type = 'Owner'
        self._api_type = 'owners'
        self._api_entity = 'owner'

        self._utils = Utils()
        self._tc_requests = TiTcRequest(self._tcex)

    @property
    def type(self):
        """Return main type."""
        return self._type

    @property
    def tc_requests(self):
        """Return tc request object."""
        return self._tc_requests

    @property
    def api_type(self):
        """Return api type."""
        return self._api_type

    @property
    def api_entity(self):
        """Return api entity."""
        return self._api_entity

    @api_entity.setter
    def api_entity(self, api_entity):
        """Set the Api Entity

        Args:
            api_entity:

        Returns:

        """
        self._api_entity = api_entity

    @api_type.setter
    def api_type(self, api_type):
        """Set the Api Type

        Args:
            api_type:

        Returns:

        """
        self._api_type = api_type

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """Set the Tc Request Object

        Args:
            tc_requests:

        Returns:

        """
        self._tc_requests = tc_requests

    def many(self):
        """Get all of the owners available.

        Args:
        """
        yield from self.tc_requests.many(self.api_type, None, self.api_entity)

    def mine(self):
        """Get all of my owners available.

        Returns:

        """
        return self.tc_requests.mine()

    def members(self):
        """Get all members for my owners

        Returns:

        """
        yield from self.tc_requests.many(self.api_type, 'mine/members', 'user')

    def metrics(self):
        """Get all the metrics for owners

        Returns:

        """
        yield from self.tc_requests.many(self.api_type, 'metrics', 'ownerMetric')
