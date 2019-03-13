from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class Address(Indicator):
    """ThreatConnect Batch Address Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, ip, **kwargs):
        """Initialize Class Properties.

        Args:
            ip (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(Address, self).__init__(tcex, 'addresses', ip, **kwargs)
        self._data['ip'] = ip

    def dns_resolution(self):
        return self.tc_requests.dns_resolution(self.api_type, self.api_sub_type, self.unique_id)

