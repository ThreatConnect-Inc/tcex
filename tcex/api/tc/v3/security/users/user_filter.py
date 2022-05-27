"""User TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class UserFilter(FilterABC):
    """Filter Object for Users"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.USERS.value

    def first_name(self, operator: Enum, first_name: str):
        """Filter First Name based on **firstName** keyword.

        Args:
            operator: The operator enum for the filter.
            first_name: The first name of the user.
        """
        self._tql.add_filter('firstName', operator, first_name, TqlType.STRING)

    def group_id(self, operator: Enum, group_id: int):
        """Filter groupID based on **groupId** keyword.

        Args:
            operator: The operator enum for the filter.
            group_id: The ID of the group the user belongs to.
        """
        self._tql.add_filter('groupId', operator, group_id, TqlType.INTEGER)

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the user.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def last_name(self, operator: Enum, last_name: str):
        """Filter Last Name based on **lastName** keyword.

        Args:
            operator: The operator enum for the filter.
            last_name: The last name of the user.
        """
        self._tql.add_filter('lastName', operator, last_name, TqlType.STRING)

    def user_name(self, operator: Enum, user_name: str):
        """Filter User Name based on **userName** keyword.

        Args:
            operator: The operator enum for the filter.
            user_name: The user name of the user.
        """
        self._tql.add_filter('userName', operator, user_name, TqlType.STRING)
