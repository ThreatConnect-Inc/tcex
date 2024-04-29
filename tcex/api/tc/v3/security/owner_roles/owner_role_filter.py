"""TcEx Framework Module"""

# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class OwnerRoleFilter(FilterABC):
    """Filter Object for OwnerRoles"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.OWNER_ROLES.value

    def available(self, operator: Enum, available: bool):
        """Filter Available based on **available** keyword.

        Args:
            operator: The operator enum for the filter.
            available: The availability status of the role.
        """
        self._tql.add_filter('available', operator, available, TqlType.BOOLEAN)

    def comm_role(self, operator: Enum, comm_role: bool):
        """Filter Community Role based on **commRole** keyword.

        Args:
            operator: The operator enum for the filter.
            comm_role: The scope of the role.
        """
        self._tql.add_filter('commRole', operator, comm_role, TqlType.BOOLEAN)

    def description_admin(self, operator: Enum, description_admin: list | str):
        """Filter Admin Description based on **descriptionAdmin** keyword.

        Args:
            operator: The operator enum for the filter.
            description_admin: The description of this role's admin access.
        """
        if isinstance(description_admin, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('descriptionAdmin', operator, description_admin, TqlType.STRING)

    def description_comm(self, operator: Enum, description_comm: list | str):
        """Filter Community Description based on **descriptionComm** keyword.

        Args:
            operator: The operator enum for the filter.
            description_comm: The description of this role's access within a community.
        """
        if isinstance(description_comm, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('descriptionComm', operator, description_comm, TqlType.STRING)

    def description_org(self, operator: Enum, description_org: list | str):
        """Filter Organization Description based on **descriptionOrg** keyword.

        Args:
            operator: The operator enum for the filter.
            description_org: The description of this role's access within an organization.
        """
        if isinstance(description_org, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('descriptionOrg', operator, description_org, TqlType.STRING)

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the user.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def name(self, operator: Enum, name: list | str):
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the role.
        """
        if isinstance(name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def org_role(self, operator: Enum, org_role: bool):
        """Filter Organization Role based on **orgRole** keyword.

        Args:
            operator: The operator enum for the filter.
            org_role: The scope of this role.
        """
        self._tql.add_filter('orgRole', operator, org_role, TqlType.BOOLEAN)

    def version(self, operator: Enum, version: int | list):
        """Filter Version based on **version** keyword.

        Args:
            operator: The operator enum for the filter.
            version: The version number of the role.
        """
        if isinstance(version, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('version', operator, version, TqlType.INTEGER)
