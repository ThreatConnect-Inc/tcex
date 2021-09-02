"""Artifact Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.security.filters.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class FilterUser(FilterABC):
    """Artifact Filter"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.USERS.value

    def first_name(self, operator: Enum, first_name: str) -> None:
        """Filter Artifacts based on **analytics score** keyword.

        Args:
            operator: The operator enum for the filter.
            first_name: The score value to use for filtering.
        """
        self._tql.add_filter('firstName', operator, first_name, TQL.Type.STRING)

    def group_id(self, operator: Enum, group_id: int) -> None:
        """Filter Artifacts based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case associated with this artifact.
        """
        self._tql.add_filter('groupId', operator, group_id, TQL.Type.INTEGER)

    def last_name(self, operator: Enum, last_name: str):
        """Filter Artifact based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the artifact was written.
        """
        self._tql.add_filter('lastName', operator, last_name, TQL.Type.STRING)

    def id(self, operator: Enum, id_: int):
        """Filter Artifacts based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id_: The ID of the artifact.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def user_name(self, operator, user_name: str):
        """Filter Tasks based on **automated** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            active (bool): A flag indicating whether or not the artifact is active.
        """
        self._tql.add_filter('userName', operator, user_name, TQL.Type.STRING)
