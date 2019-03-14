from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import Indicator


class RegistryKey(Indicator):
    """ThreatConnect Batch Registry Key Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, key_name, value_name, value_type, **kwargs):
        """Initialize Class Properties.

        Args:
            key_name (str): The key_name value for this Indicator.
            value_name (str): The value_name value for this Indicator.
            value_type (str): The value_type value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        summary = self.build_summary(key_name, value_name, value_type)
        super(RegistryKey, self).__init__('Registry Key', summary, **kwargs)
