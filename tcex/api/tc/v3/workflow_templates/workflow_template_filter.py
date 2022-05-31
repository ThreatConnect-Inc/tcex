"""Workflow_Template TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class WorkflowTemplateFilter(FilterABC):
    """Filter Object for WorkflowTemplates"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.WORKFLOW_TEMPLATES.value

    def active(self, operator: Enum, active: bool):
        """Filter Active based on **active** keyword.

        Args:
            operator: The operator enum for the filter.
            active: The active status of this template.
        """
        self._tql.add_filter('active', operator, active, TqlType.BOOLEAN)

    def description(self, operator: Enum, description: str):
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of this template.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the template.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def name(self, operator: Enum, name: str):
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of this template.
        """
        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def owner(self, operator: Enum, owner: int):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the template.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name for the template.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def target_id(self, operator: Enum, target_id: int):
        """Filter Target ID based on **targetId** keyword.

        Args:
            operator: The operator enum for the filter.
            target_id: The assigned user or group ID for the template.
        """
        self._tql.add_filter('targetId', operator, target_id, TqlType.INTEGER)

    def target_type(self, operator: Enum, target_type: str):
        """Filter Target Type based on **targetType** keyword.

        Args:
            operator: The operator enum for the filter.
            target_type: The target type for this template (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TqlType.STRING)

    def version(self, operator: Enum, version: int):
        """Filter Version based on **version** keyword.

        Args:
            operator: The operator enum for the filter.
            version: The version of this template.
        """
        self._tql.add_filter('version', operator, version, TqlType.INTEGER)
