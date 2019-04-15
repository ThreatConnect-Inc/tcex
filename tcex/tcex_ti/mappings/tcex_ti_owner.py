# -*- coding: utf-8 -*-
"""ThreatConnect TI Generic Mappings Object"""
from tcex.tcex_ti.tcex_ti_tc_request import TiTcRequest
from tcex.tcex_utils import TcExUtils


class Owner(object):
    """Common API calls for for Indicators/SecurityLabels/Groups and Victims"""

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            tcex:
        """
        self._tcex = tcex
        self._data = {}

        self._type = 'Owner'
        self._api_type = 'owners'
        self._api_entity = 'owner'

        self._utils = TcExUtils()
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
        """
        Sets the Api Entity
        Args:
            api_entity:

        Returns:

        """
        self._api_entity = api_entity

    @api_type.setter
    def api_type(self, api_type):
        """
        Sets the Api Type
        Args:
            api_type:

        Returns:

        """
        self._api_type = api_type

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """
        Sets the Tc Request Object
        Args:
            tc_requests:

        Returns:

        """
        self._tc_requests = tc_requests

    def many(self):
        """
        Gets all of the owners available.

        Args:
        """
        for i in self.tc_requests.many(self.api_type, None, self.api_entity):
            yield i

    def mine(self):
        """
        Gets all of my owners available.
        Returns:

        """
        return self.tc_requests.mine()

    def members(self):
        """
        Gets all members for my owners
        Returns:

        """
        for i in self.tc_requests.many(self.api_type, 'mine/members', 'user'):
            yield i

    def metrics(self):
        """
        Gets all the metrics for owners
        Returns:

        """
        for i in self.tc_requests.many(self.api_type, 'metrics', 'ownerMetric'):
            yield i
