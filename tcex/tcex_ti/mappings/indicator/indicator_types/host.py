from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class Host(Indicator):
    """ThreatConnect Batch Host Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, hostname, **kwargs):
        """Initialize Class Properties.

        Args:
            hostname (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
            whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(Host, self).__init__(tcex, 'hosts', **kwargs)
        self.api_entity = 'host'
        self._data['hostName'] = hostname

    def can_create(self):
        if self.data.get('hostName'):
            return True
        return False

    def _set_unique_id(self, json_response):
        self.unique_id = json_response.get('hostName', '')

    def dns_resolution(self):
        return self.tc_requests.dns_resolution(self.api_type, self.api_sub_type, self.unique_id)
