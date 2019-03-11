from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group


class Incident(Group):
    """ThreatConnect Batch Incident Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Valid Values:
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
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super(Incident, self).__init__(tcex, 'incidents', name, **kwargs)

    @property
    def event_date(self):
        """Return Incident event date."""
        return self._data.get('eventDate')

    @event_date.setter
    def event_date(self, event_date):
        """Set Incident event_date."""
        self._data['eventDate'] = self._utils.format_datetime(
            event_date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def status(self):
        """Return Incident status."""
        return self._data.get('status')

    @status.setter
    def status(self, status):
        """Set Incident status.

        Valid Values:
        + New
        + Open
        + Stalled
        + Containment Achieved
        + Restoration Achieved
        + Incident Reported
        + Closed
        + Rejected
        + Deleted
        """
        self._data['status'] = status

