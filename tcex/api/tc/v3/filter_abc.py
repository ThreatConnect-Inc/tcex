"""Case Management Filter Abstract Base Class"""
# standard library
from abc import ABC
from typing import List

# third-party
from tcex.api.tql import TQL


class FilterABC(ABC):
    """Case Management Filter Abstract Base Class"""

    def __init__(self):
        """Initialize Class properties"""
        self._tql = TQL()

    @property
    def _api_endpoint(self):
        raise NotImplementedError('Child class must implement this method.')

    @property
    def implemented_keywords(self) -> List[str]:
        """Return implemented TQL keywords."""
        keywords = []
        for prop in dir(self):
            if prop.startswith('_') or prop in ['tql']:
                continue
            keywords.append(prop)

        return keywords

    @property
    def keywords(self) -> List[str]:
        """Return supported TQL keywords."""
        return [td.get('keyword') for td in self.tql_data]

    @property
    def tql(self):
        return self._tql

    @tql.setter
    def tql(self, tql: str) -> None:
        """Filter objects based on TQL expression.

        Args:
            tql: The raw TQL string for the filter.
        """
        self.tql.set_raw_tql(tql)

    def __str__(self) -> str:
        return self.tql.raw_tql or self.tql.as_str
