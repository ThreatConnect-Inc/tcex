"""Case Management Filter Abstract Base Class"""
# standard library
from abc import ABC
from typing import TYPE_CHECKING, List

# third-party
from requests import Session

# first-party
from tcex.backports import cached_property

if TYPE_CHECKING:
    # first-party
    from tcex.case_management.tql import TQL


class FilterABC(ABC):
    """Case Management Filter Abstract Base Class"""

    def __init__(self, session: Session, tql: 'TQL'):
        """Initialize Class properties"""
        self._session = session
        self._tql = tql

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

    def tql(self, tql: str) -> None:
        """Filter objects based on TQL expression.

        Args:
            tql: The raw TQL string for the filter.
        """
        self._tql.set_raw_tql(tql)

    @cached_property
    def tql_data(self) -> dict:
        """Return TQL data keywords."""
        _tql_data = None
        r = self._session.options(f'{self._api_endpoint}/tql', params={})
        if r.ok:
            _tql_data = r.json()['data']
        # print('\nTQL DATA:', _tql_data)
        return _tql_data
