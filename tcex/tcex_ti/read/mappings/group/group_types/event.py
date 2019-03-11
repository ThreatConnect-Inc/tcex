from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group


class Event(Group):
    """ThreatConnect Batch Event Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex):
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
        super(Event, self).__init__(tcex, 'events')

    def status(self, status):
        """Return Email to."""
        self._data['status'] = status
        request = self._base_request()
        request['status'] = status
        return self._tc_requests.update(request)

    def event_date(self, event_date):
        """Return Email to."""
        event_date = self._utils.format_datetime(
            event_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
        self._data['eventDate'] = event_date
        request = self._base_request()
        request['eventDate'] = event_date
        return self._tc_requests.update(request)

