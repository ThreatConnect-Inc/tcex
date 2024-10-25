"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


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
        ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
        event_date (str, kwargs): The incident event date expression for this Group.
        name (str, kwargs): [Required for Create] The name for this Group.
        status (str, kwargs): The status for this Group.
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties."""
        super().__init__(
            ti, sub_type='Incident', api_entity='incident', api_branch='incidents', **kwargs
        )

    def event_date(self, event_date):
        """Update the event_date.

        Args:
            event_date: Converted to %Y-%m-%dT%H:%M:%SZ date format.
        """
        if not self.can_update():
            self._handle_error(910, [self.type])

        event_date = self.util.any_to_datetime(event_date).strftime('%Y-%m-%dT%H:%M:%SZ')
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
        """
        if not self.can_update():
            self._handle_error(910, [self.type])

        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
