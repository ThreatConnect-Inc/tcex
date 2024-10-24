"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class Event(Group):
    """Unique API calls for Event API Endpoints

    Valid status:
    + Escalated
    + False Positive
    + Needs Review
    + No Further Action

    Args:
        ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
        event_date (str, kwargs): The event "event date" datetime expression for this Group.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
        status (str, kwargs): The status for this Group.
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties."""
        super().__init__(ti, sub_type='Event', api_entity='event', api_branch='events', **kwargs)

    def event_date(self, event_date):
        """Update the event date for the Event.

        Args:
            event_date (str): The event datetime expression for this Group.

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._handle_error(910, [self.type])

        event_date = self.util.any_to_datetime(event_date).strftime('%Y-%m-%dT%H:%M:%SZ')
        self._data['eventDate'] = event_date
        request = {'eventDate': event_date}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)

    def status(self, status):
        """Update the event date for the Event.

        Valid status:
        + Escalated
        + False Positive
        + Needs Review
        + No Further Action

        Args:
            status (str, kwargs): The status for this Group.

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._handle_error(910, [self.type])

        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
