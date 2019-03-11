from tcex.tcex_ti.read.mappings.indicator.tcex_ti_indicator import Indicator


class Address(Indicator):
    """ThreatConnect Batch Address Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = []

    def __init__(self, tcex, owner, unique_id=None):
        super(Address, self).__init__(tcex, 'addresses', owner, unique_id=unique_id)

