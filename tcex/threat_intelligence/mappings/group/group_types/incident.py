# -*- coding: utf-8 -*-
"""ThreatConnect TI Incident"""
from ..group import Group


class Incident(Group):
    """Unique API calls for Incident API Endpoints

    Valid status:
    + Closed
    + Containment Achieved
    + Deleted
    + Incident Reported
    + Open
    + New
    + Rejected
    + Restoration Achieved
    + Stalled

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        event_date (str, kwargs): The incident event date expression for this Group.
        name (str, kwargs): [Required for Create] The name for this Group.
        status (str, kwargs): The status for this Group.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class Properties."""
        super().__init__(
            tcex, sub_type='Incident', api_entity='incident', api_branch='incidents', **kwargs
        )

    def event_date(self, event_date):
        """Update the event_date.

        Args:
            event_date: Converted to %Y-%m-%dT%H:%M:%SZ date format.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        event_date = self._utils.datetime.format_datetime(
            event_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
        self._data['eventDate'] = event_date
        request = {'eventDate': event_date}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def status(self, status):
        """Update  the incidents status

        Valid status:
        + Closed
        + Containment Achieved
        + Deleted
        + Incident Reported
        + Open
        + New
        + Rejected
        + Restoration Achieved
        + Stalled

        Args:
            status: Closed, Containment Achieved, Deleted, Incident Reported, Open, New, Rejected,
            Restoration Achieved, Stalled.

        Returns:

        """
        if not self.can_update():
            self._tcex.handle_error(910, [self.type])

        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
