from tcex.tcex_ti.write.mappings.group.tcex_ti_group import Group


class Signature(Group):
    """ThreatConnect Batch Signature Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex):
        super(Signature, self).__init__(tcex, 'signatures')

