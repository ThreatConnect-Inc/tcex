"""TcEx Framework Module"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class AttributeTypeFilter(FilterABC):
    """Filter Object for AttributeTypes"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.ATTRIBUTE_TYPES.value

    def associated_type(self, operator: Enum, associated_type: list | str):
        """Filter Associated Type based on **associatedType** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_type: The data type(s) that the attribute type can be used for.
        """
        if isinstance(associated_type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('associatedType', operator, associated_type, TqlType.STRING)

    def description(self, operator: Enum, description: list | str):
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the attribute type.
        """
        if isinstance(description, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the attribute type.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def maxsize(self, operator: Enum, maxsize: int | list):
        """Filter Maxsize based on **maxsize** keyword.

        Args:
            operator: The operator enum for the filter.
            maxsize: Max size of the attribute.
        """
        if isinstance(maxsize, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('maxsize', operator, maxsize, TqlType.INTEGER)

    def name(self, operator: Enum, name: list | str):
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the attribute type.
        """
        if isinstance(name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def owner(self, operator: Enum, owner: int | list):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the attribute type.
        """
        if isinstance(owner, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: list | str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the attribute type.
        """
        if isinstance(owner_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def system(self, operator: Enum, system: bool):
        """Filter SystemLevel based on **system** keyword.

        Args:
            operator: The operator enum for the filter.
            system: A flag to show System level attributes (TRUE) or owner-specific ones only
                (FALSE).
        """
        self._tql.add_filter('system', operator, system, TqlType.BOOLEAN)
