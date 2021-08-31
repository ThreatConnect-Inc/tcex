"""ThreatConnect Adversary"""
# first-party
from tcex.api.v3.threat_intelligence.group.group_collection_abc import GroupCollectionABC
from tcex.api.v3.threat_intelligence.group.group_abc import GroupABC
from tcex.api.v3.threat_intelligence.group.model.adversary import Adversary as AdversaryModel
from tcex.api.tql import Operator


class Adversaries(GroupCollectionABC):
    """ThreatConnect Adversaries Object"""

    def __iter__(self):
        """Object iterator"""
        return self.iterate(base_class=Adversary)

    @property
    def _base_filter(self) -> dict:
        return {
            'keyword': 'typeName',
            'operator': Operator.IN,
            'value': '(\"Adversary\")',
            'type_': 'list',
        }


class Adversary(GroupABC):
    """Note object for Case Management."""

    def __init__(self, session, **kwargs) -> None:
        """Initialize Class properties"""
        super().__init__(session)
        kwargs['type'] = 'Adversary'
        self._model = AdversaryModel(**kwargs)
