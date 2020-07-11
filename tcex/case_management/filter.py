# -*- coding: utf-8 -*-
"""ThreatConnect Case Management Filter Module"""


class Filter:
    """Filter Base Class

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, api_endpoint, tcex, tql):
        """Initialize Class properties"""
        self._api_endpoint = api_endpoint.value
        self._tcex = tcex
        self._tql = tql
        self._tql_data = None
        self.artifacts = None

    @property
    def implemented_keywords(self):
        """Return implemented TQL keywords."""
        keywords = []
        for prop in dir(self):
            if prop.startswith('_') or prop in ['tql']:
                continue
            keywords.append(prop)

        return keywords

    @property
    def keywords(self):
        """Return supported TQL keywords."""
        return [td.get('keyword') for td in self.tql_data]

    @property
    def tql_data(self):
        """Return TQL data keywords."""
        if self._tql_data is None:
            r = self._tcex.session.options(f'{self._api_endpoint}/tql', params={})
            if r.ok:
                self._tql_data = r.json()['data']

        return self._tql_data

    def tql(self, tql):
        """Filter objects based on TQL expression.

        Args:
            tql (str): The raw TQL string for the filter.
        """
        self._tql.set_raw_tql(tql)
