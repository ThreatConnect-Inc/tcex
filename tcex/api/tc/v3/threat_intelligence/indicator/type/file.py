"""ThreatConnect File"""
# first-party
from tcex.api.v3.threat_intelligence.indicator.indicator_collection_abc import IndicatorCollectionABC
from tcex.api.v3.threat_intelligence.indicator.indicator_abc import IndicatorABC
from tcex.api.v3.threat_intelligence.indicator.model.file import File as FileModel
from tcex.api.tql import Operator


class Files(IndicatorCollectionABC):
    """ThreatConnect Files Object"""

    def __iter__(self):
        """Object iterator"""
        return self.iterate(base_class=File)

    @property
    def _base_filter(self) -> dict:
        return {
            'keyword': 'typeName',
            'operator': Operator.IN,
            'value': '(\"File\")',
            'type_': 'list',
        }


class File(IndicatorABC):
    """Note object for Case Management."""

    def __init__(self, session, **kwargs) -> None:
        """Initialize Class properties"""
        super().__init__(session)
        kwargs['type'] = 'File'
        self._model = FileModel(**kwargs)
