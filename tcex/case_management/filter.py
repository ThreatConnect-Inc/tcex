"""ThreatConnect Case Management Filter Module"""
# standard library
from typing import List

# first-party
from tcex.case_management.api_endpoints import ApiEndpoints
from tcex.case_management.tql import TQL


class Filter:
    """Filter Base Class

    Args:
        tql: Instance of TQL Class.
    """

    def __init__(self, api_endpoint: ApiEndpoints, tcex, tql: TQL):
        """Initialize Class properties"""
        self._api_endpoint = api_endpoint.value
        self._tcex = tcex
        self._tql = tql
        self._tql_data = None
        self.artifacts = None

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
    def tql_data(self) -> dict:
        """Return TQL data keywords."""
        if self._tql_data is None:
            r = self._tcex.session.options(f'{self._api_endpoint}/tql', params={})
            if r.ok:
                self._tql_data = r.json()['data']

        return self._tql_data

    def tql(self, tql: str) -> None:
        """Filter objects based on TQL expression.

        Args:
            tql: The raw TQL string for the filter.
        """
        self._tql.set_raw_tql(tql)
