# -*- coding: utf-8 -*-
"""ThreatConnect TI Security Label"""
# first-party
from tcex.utils import Utils

from ..tcex_ti_tc_request import TiTcRequest


class Tag:
    """Unique API calls for Tag API Endpoints

    Args:
        group_type (str): The ThreatConnect define Group type.
        name (str): The name for this Group.
        xid (str, kwargs): The external id for this Group.

    """

    def __init__(self, tcex, name):
        """Initialize Class Properties."""
        self._name = name
        self._tcex = tcex
        self._type = 'tags'
        self._api_sub_type = None
        self._api_type = None
        self._api_entity = 'tag'

        self._utils = Utils()
        self._tc_requests = TiTcRequest(self._tcex)

    @staticmethod
    def is_tag():
        """Return true is instance is a tag object."""
        return True

    def groups(self, group_type=None, filters=None, owner=None, params=None):
        """Get  all groups from a tag.

        Args:
            filters:
            params:
            group_type:
        """
        if group_type and group_type.lower() == 'task':
            group = self._tcex.ti.task()
        else:
            group = self._tcex.ti.group(group_type)
        return self.tc_requests.groups_from_tag(
            group, self.name, filters=filters, owner=owner, params=params
        )

    def indicators(self, indicator_type=None, filters=None, owner=None, params=None):
        """Get all indicators from a tag.

        Args:
            params:
            filters:
            indicator_type:
        """
        indicator = self._tcex.ti.indicator(indicator_type)
        yield from self.tc_requests.indicators_from_tag(
            indicator, self.name, filters=filters, owner=owner, params=params
        )

    def victims(self, filters=None, owner=None, params=None):
        """Get  all victims from a tag."""
        victim = self._tcex.ti.victim()
        yield from self.tc_requests.victims_from_tag(
            victim, self.name, filters=filters, owner=owner, params=params
        )

    @property
    def name(self):
        """Get the tag name."""
        return self._name

    @property
    def tc_requests(self):
        """Get the tc request object"""
        return self._tc_requests

    @name.setter
    def name(self, name):
        """Set  the tag name

        Args:
            name:

        Returns:

        """
        self._name = name

    @tc_requests.setter
    def tc_requests(self, tc_requests):
        """Set the tc request object.

        Args:
            tc_requests:

        Returns:

        """
        self._tc_requests = tc_requests
