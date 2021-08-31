"""ThreatConnect File"""
# first-party
from tcex.api.v3.threat_intelligence.indicator.indicator_collection_abc import IndicatorCollectionABC


class Indicators(IndicatorCollectionABC):
    """ThreatConnect Files Object"""

    def __iter__(self):
        """Object iterator"""
        return self.iterate()

    @property
    def _base_filter(self) -> dict:
        return {}