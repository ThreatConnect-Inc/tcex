from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group


class Signature(Group):
    """ThreatConnect Batch Signature Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, name, file_name, file_type, file_text, **kwargs):
        """Initialize Class Properties.

        Valid file_types:
        + Snort ®
        + Suricata
        + YARA
        + ClamAV ®
        + OpenIOC
        + CybOX ™
        + Bro
        + Regex
        + SPL - Splunk ® Search Processing Language

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached signature for this Group.
            file_type (str): The signature type for this Group.
            file_text (str): The signature content for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super(Signature, self).__init__(tcex, 'signatures', name, **kwargs)
        self._data['fileName'] = file_name
        self._data['fileType'] = file_type
        self._data['fileText'] = file_text

