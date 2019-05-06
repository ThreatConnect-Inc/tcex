# -*- coding: utf-8 -*-
"""ThreatConnect TI Campaign """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Campaign(Group):
    """Unique API calls for Campaign API Endpoints"""

    def __init__(self, tcex, name, owner=None, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            first_seen (str, kwargs): The first seen datetime expression for this Group.
        """
        super(Campaign, self).__init__(
            tcex, 'Campaign', 'campaign', 'campaigns', name, owner, **kwargs
        )

    def first_seen(self, first_seen):
        """
        Updates the campaign with the new first_seen date.

        Args:
            first_seen: The first_seen date. Converted to %Y-%m-%dT%H:%M:%SZ date format

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        first_seen = self._utils.format_datetime(first_seen, date_format='%Y-%m-%dT%H:%M:%SZ')
        self._data['firstSeen'] = first_seen
        request = {'firstSeen': first_seen}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
