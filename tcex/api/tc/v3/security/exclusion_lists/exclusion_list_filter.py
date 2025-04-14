"""TcEx Framework Module"""

# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class ExclusionListFilter(FilterABC):
    """Filter Object for ExclusionLists"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.EXCLUSION_LISTS.value

    def active(self, operator: Enum, active: bool):
        """Filter Active based on **active** keyword.

        Args:
            operator: The operator enum for the filter.
            active: The active status of the exclusion.
        """
        self._tql.add_filter('active', operator, active, TqlType.BOOLEAN)

    def id(self, operator: Enum, id: int | list):  # noqa: A002
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the exclusion list.
        """
        if isinstance(id, list) and operator not in self.list_types:
            ex_msg = (
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )
            raise RuntimeError(ex_msg)

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def managed(self, operator: Enum, managed: bool):
        """Filter Managed based on **managed** keyword.

        Args:
            operator: The operator enum for the filter.
            managed: Whether the exclusion list is managed by System.
        """
        self._tql.add_filter('managed', operator, managed, TqlType.BOOLEAN)

    def name(self, operator: Enum, name: list | str):
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The exclusion list mapping field.
        """
        if isinstance(name, list) and operator not in self.list_types:
            ex_msg = (
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )
            raise RuntimeError(ex_msg)

        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def owner(self, operator: Enum, owner: int | list):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the exclusion list.
        """
        if isinstance(owner, list) and operator not in self.list_types:
            ex_msg = (
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )
            raise RuntimeError(ex_msg)

        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)
