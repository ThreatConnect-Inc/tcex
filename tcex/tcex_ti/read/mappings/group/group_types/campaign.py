from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group


class Campaign(Group):
    """ThreatConnect Batch Campaign Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            first_seen (str, kwargs): The first seen datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super(Campaign, self).__init__(tcex, 'campaigns')

    def first_seen(self, first_seen):
        """Set Document first seen."""
        first_seen = self._utils.format_datetime(
            first_seen, date_format='%Y-%m-%dT%H:%M:%SZ'
        )
        self._data['firstSeen'] = first_seen
        request = {'firstSeen': first_seen}
        return self._tc_requests.update(self.type, self.api_sub_type, self.unique_id, request)


