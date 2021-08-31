"""ThreatConnect Adversary"""
# first-party
from tcex.api.v3.threat_intelligence.group.group_collection_abc import GroupCollectionABC
from tcex.api.v3.threat_intelligence.group.group import Group


class Groups(GroupCollectionABC):
    """ThreatConnect Adversaries Object"""

    def __iter__(self):
        """Object iterator"""
        return self.iterate(base_class=Group)

    @property
    def _base_filter(self) -> dict:
        return {}
