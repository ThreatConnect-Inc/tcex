"""Case Management Filter Abstract Base Class"""
# standard library
from abc import ABC
from typing import TYPE_CHECKING, List

# first-party
from tcex.utils.utils import Utils

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v3.tql.tql import Tql


class FilterABC(ABC):
    """Case Management Filter Abstract Base Class"""

    def __init__(self, tql: 'Tql'):
        """Initialize Class properties"""
        self._tql = tql

        # properties
        self.utils = Utils()

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
    def tql(self) -> 'Tql':
        """Return the current TQL instance."""
        return self._tql

    @tql.setter
    def tql(self, tql: str):
        """Filter objects based on TQL expression.

        Args:
            tql: The raw TQL string for the filter.
        """
        self.tql.set_raw_tql(tql)

    def __str__(self) -> str:
        """Return string representation of TQL."""
        return self.tql.raw_tql or self.tql.as_str
