from tcex.tcex_ti.write.mappings.indicator.tcex_ti_indicator import Indicator


class ASN(Indicator):
    """ThreatConnect Batch ASN Object."""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, as_number, **kwargs):
        """Initialize Class Properties.

        Args:
            as_number (str): The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(ASN, self).__init__(tcex, 'asns', as_number, **kwargs)
        self._data['as_number'] = as_number

