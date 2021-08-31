"""Artifact Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.v3.threat_intelligence.indicator.api_endpoints import ApiEndpoints
from tcex.api.v3.filter_abc import FilterABC
from tcex.api.tql import Type


class Indicator(FilterABC):
    """Artifact Filter"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.INDICATORS.value

    def id(self, operator: Enum, id_: int):
        self._tql.add_filter('id', operator, id_, Type.INTEGER)

    def type_name(self, operator: Enum, type_name: str):
        self._tql.add_filter('typeName', operator, type_name, Type.STRING)
