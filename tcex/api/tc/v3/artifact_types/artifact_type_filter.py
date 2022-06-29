"""Artifact_Type TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class ArtifactTypeFilter(FilterABC):
    """Filter Object for ArtifactTypes"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.ARTIFACT_TYPES.value

    def active(self, operator: Enum, active: bool):
        """Filter Active based on **active** keyword.

        Args:
            operator: The operator enum for the filter.
            active: The active status of the artifact type.
        """
        self._tql.add_filter('active', operator, active, TqlType.BOOLEAN)

    def data_type(self, operator: Enum, data_type: str):
        """Filter Data Type based on **dataType** keyword.

        Args:
            operator: The operator enum for the filter.
            data_type: The data type of the artifact type.
        """
        self._tql.add_filter('dataType', operator, data_type, TqlType.STRING)

    def description(self, operator: Enum, description: str):
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the artifact type.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the artifact type.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def intel_type(self, operator: Enum, intel_type: str):
        """Filter Intel Type based on **intelType** keyword.

        Args:
            operator: The operator enum for the filter.
            intel_type: The intel type of the artifact type.
        """
        self._tql.add_filter('intelType', operator, intel_type, TqlType.STRING)

    def managed(self, operator: Enum, managed: bool):
        """Filter Managed based on **managed** keyword.

        Args:
            operator: The operator enum for the filter.
            managed: The managed status of the artifact type.
        """
        self._tql.add_filter('managed', operator, managed, TqlType.BOOLEAN)

    def name(self, operator: Enum, name: str):
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the artifact type.
        """
        self._tql.add_filter('name', operator, name, TqlType.STRING)
