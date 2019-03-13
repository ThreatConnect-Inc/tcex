from tcex.tcex_ti.mappings.group import Group


class Threat(Group):
    """ThreatConnect Batch Threat Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, name, **kwargs):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super(Threat, self).__init__(tcex, 'threats', name, **kwargs)

