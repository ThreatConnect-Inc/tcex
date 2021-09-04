"""Artifact Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.security.filters.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class FilterUserGroup(FilterABC):
    """Artifact Filter"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.USERS.value

    def description(self, operator: Enum, description: str) -> None:
        """Filter Artifacts based on **analytics score** keyword.

        Args:
            operator: The operator enum for the filter.
            first_name: The score value to use for filtering.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    def name(self, operator: Enum, name: str):
        """Filter Artifact based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the artifact was written.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def id(self, operator: Enum, id_: int):
        """Filter Artifacts based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id_: The ID of the artifact.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)
