from tcex.tcex_ti.write.mappings.indicator.tcex_ti_indicator import Indicator


class URL(Indicator):
    """ThreatConnect Batch URL Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex):
        super(URL, self).__init__(tcex, 'urls')
