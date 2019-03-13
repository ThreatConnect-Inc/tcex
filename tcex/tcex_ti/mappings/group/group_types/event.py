from tcex.tcex_ti.mappings.group import Group


class Event(Group):
    """ThreatConnect Batch Event Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Valid Values:
        + Escalated
        + False Positive
        + Needs Review
        + No Further Action

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super(Event, self).__init__(tcex, 'events', name, **kwargs)

    def status(self, status):
        """Return Email to."""
        self._data['status'] = status
        request = {'status': status}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

    def event_date(self, event_date):
        """Return Email to."""
        event_date = self._utils.format_datetime(
            event_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
        self._data['eventDate'] = event_date
        request = {'eventDate': event_date}
        return self.tc_requests.update(self.api_type, self.api_sub_type, self.unique_id, request)

