"""Case Management Collection Abstract Base Class"""
# standard library
from tcex.api.v3.threat_intelligence.threat_intelligence_collection_abc import ThreatIntelligenceCollectionABC
from tcex.api.v3.threat_intelligence.group.api_endpoints import ApiEndpoints
from tcex.api.v3.threat_intelligence.group.filter.group import Group as GroupFilter


class GroupCollectionABC(ThreatIntelligenceCollectionABC):
    """Group Collection Abstract Base Class."""

    @property
    def filter(self):  # pragma: no cover
        """Return filter method."""
        if not self._filter:
            self._filter = GroupFilter()
            if self._base_filter:
                self._filter._tql.add_filter(**self._base_filter)
        return self._filter

    @property
    def _base_filter(self):
        raise NotImplementedError('Child class must implement this method.')

    @property
    def _api_endpoint(self) -> None:  # pragma: no cover
        """Return filter method."""
        return ApiEndpoints.GROUPS.value
