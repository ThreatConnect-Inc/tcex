# -*- coding: utf-8 -*-
"""ThreatConnect TI Security Label"""

# import local modules for dynamic reference
from tcex.tcex_ti.tcex_ti_tc_request import TiTcRequest
from tcex.tcex_utils import TcExUtils


class Tag(object):
    """Unique API calls for Tag API Endpoints"""

    def __init__(self, tcex, name):
        """Initialize Class Properties.

        Args:
            group_type (str): The ThreatConnect define Group type.
            name (str): The name for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        self._name = name
        self._tcex = tcex
        self._type = 'tags'
        self._api_sub_type = None
        self._api_type = None
        self._api_entity = 'tag'

        self._utils = TcExUtils()
        self._tc_requests = TiTcRequest(self._tcex)

    @staticmethod
    def is_tag():
        """
        Indicates that this is a tag object
        Returns:

        """
        return True

    def groups(self, group_type=None, filters=None, params=None):
        """
        Gets all groups from a tag.

        Args:
            filters:
            params:
            group_type:
        """
        group = self._tcex.ti.group(group_type)
        for g in self.tc_requests.groups_from_tag(group, self.name, filters=filters, params=params):
            yield g

    def indicators(self, indicator_type=None, filters=None, params=None):
        """
        Gets all indicators from a tag.

        Args:
            params:
            filters:
            indicator_type:
        """
        indicator = self._tcex.ti.indicator(indicator_type)
        for i in self.tc_requests.indicators_from_tag(
            indicator, self.name, filters=filters, params=params
        ):
            yield i

    def victims(self, filters=None, params=None):
        """
        Gets all victims from a tag.
        """
        victim = self._tcex.ti.victim(None)
        for v in self.tc_requests.victims_from_tag(
            victim, self.name, filters=filters, params=params
        ):
            yield v

    @property
    def name(self):
        """
        Gets the tag name.
        """
        return self._name

    @property
    def tc_requests(self):
        """
        Gets the tc request object
        """
        return self._tc_requests

    @name.setter
    def name(self, name):
        """
        Sets the tag name

        Args:
            name:

        Returns:

        """
        self._name = name

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """
        Sets the tc request object.

        Args:
            tc_requests:

        Returns:

        """
        self._tc_requests = tc_requests
