# -*- coding: utf-8 -*-
"""ThreatConnect TI Event """
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group


class Event(Group):
    """Unique API calls for Event API Endpoints"""

    def __init__(self, tcex, name, owner=None, **kwargs):
        """Initialize Class Properties.

        Valid status:
        + Escalated
        + False Positive
        + Needs Review
        + No Further Action

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
        """
        super(Event, self).__init__(tcex, 'Event', 'event', 'events', name, owner, **kwargs)

    def status(self, status):
        """
        Updates the events status.

        Valid status:
        + Escalated
        + False Positive
        + Needs Review
        + No Further Action

        Args:
            status: Escalated, False Positive, Needs Review, No Further Action

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def event_date(self, event_date):
        """
        Updates the events event_date.

        Args:
            event_date: Converted to %Y-%m-%dT%H:%M:%SZ date format

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        event_date = self._utils.format_datetime(event_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        self._data['eventDate'] = event_date
        request = {'eventDate': event_date}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
