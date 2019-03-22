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

    def groups(self, group_type=None):
        """

        :param group_type:
        :return:
        """
        return self.tc_requests.groups_from_tag(group_type, self.name)

    def indicators(self, indicator_type=None):
        """

        :param indicator_type:
        :return:
        """
        return self.tc_requests.indicators_from_tag(indicator_type, self.name)

    def victims(self):
        """
        :return:
        """
        return self.tc_requests.victims_from_tag(self.name)

    @property
    def name(self):
        """

        :return:
        """
        return self._name

    @property
    def tc_requests(self):
        """

        :return:
        """
        return self._tc_requests

    @name.setter
    def name(self, name):
        self._name = name

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """

        :param tc_requests:
        """
        self._tc_requests = tc_requests
