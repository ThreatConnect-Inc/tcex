"""TcEx Framework Module"""

# standard library
from abc import ABC
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.util.util import Util

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v3.tql.tql import Tql  # CIRCULAR-IMPORT


class FilterABC(ABC):
    """Case Management Filter Abstract Base Class"""

    def __init__(self, tql: 'Tql'):
        """Initialize instance properties"""
        self._tql = tql

        # properties
        self.util = Util()

    @property
    def _api_endpoint(self):
        raise NotImplementedError('Child class must implement this method.')

    @property
    def implemented_keywords(self) -> list[str]:
        """Return implemented TQL keywords."""
        keywords = []
        for prop in dir(self):
            if prop.startswith('_') or prop in ['tql']:
                continue
            keywords.append(prop)

        return keywords

    @property
    def list_types(self) -> list[TqlOperator]:
        """Return list of implemented TQL keywords that are list types."""
        return [
            TqlOperator.IN,
            TqlOperator.NOT_IN,
            TqlOperator.CONTAINS,
            TqlOperator.NOT_CONTAINS,
        ]

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
