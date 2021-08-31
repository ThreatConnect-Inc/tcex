"""Tag Filter"""
# standard library
from enum import Enum

# first-party
from tcex.case_management.api_endpoints import ApiEndpoints
from tcex.case_management.filter_abc import FilterABC
from tcex.case_management.tql import TQL


class FilterTag(FilterABC):
    """Filter Object for Tags"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TAGS.value

    def case_id(self, operator, case_id):
        """Filter Tags based on **caseId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case the tag is applied to.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def description(self, operator, description):
        """Filter Tags based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of the tag.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    # TODO: [low] cyclic import typing
    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        # first-party
        from tcex.case_management.filter_case import FilterCase

        cases = FilterCase(self._session, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Tags based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the tag.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def last_used(self, operator, last_used):
        """Filter Tags based on **lastUsed** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            last_used (str): The date this tag was last used.
        """
        self._tql.add_filter('lastUsed', operator, last_used, TQL.Type.STRING)

    def name(self, operator, name):
        """Filter Tags based on **name** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            name (str): The name of the tag.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def owner(self, operator, owner):
        """Filter Tags based on **owner** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner (int): The ID of the tag's Organization.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator: Enum, owner_name):
        """Filter Tags based on **ownerName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner_name (str): The name of the tag's Organization.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)
