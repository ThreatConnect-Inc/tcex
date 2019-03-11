from tcex.tcex_ti.write.mappings.indicator.tcex_ti_indicator import Indicator


class Host(Indicator):
    """ThreatConnect Batch Host Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex):
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
        super(Host, self).__init__(tcex, 'hosts')

    @property
    def dns_active(self):
        """Return Indicator dns active."""
        return self._indicator_data.get('flag1')

    @dns_active.setter
    def dns_active(self, dns_active):
        """Set Indicator dns active."""
        self._indicator_data['flag1'] = dns_active

    @property
    def whois_active(self):
        """Return Indicator whois active."""
        return self._indicator_data.get('flag2')

    @whois_active.setter
    def whois_active(self, whois_active):
        """Set Indicator whois active."""
        self._indicator_data['flag2'] = whois_active

