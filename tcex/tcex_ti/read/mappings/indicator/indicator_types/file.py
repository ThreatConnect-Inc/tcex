import json
import uuid

from tcex.tcex_ti.write.mappings.indicator.tcex_ti_indicator import Indicator


class File(Indicator):
    """ThreatConnect Batch File Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            md5 (str, optional): The md5 value for this Indicator.
            sha1 (str, optional): The sha1 value for this Indicator.
            sha256 (str, optional): The sha256 value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            size (str, kwargs): The file size for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super(File, self).__init__(tcex, 'files')
