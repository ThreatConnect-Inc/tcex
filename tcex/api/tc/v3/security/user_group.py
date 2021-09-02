"""User"""
# standard library
from typing import TYPE_CHECKING, Any, Optional

# third-party
from pydantic import BaseModel, Extra, Field, PrivateAttr
from requests import Session

# first-party
from tcex.security.filters.filter_user_group import FilterUserGroup
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.security.security_abc import SecurityABC
from tcex.security.security_collection_abc import SecurityCollectionABC
from tcex.security.models.user_group_model import UserGroupModel, UserGroupsModel


class UserGroups(SecurityCollectionABC):
    """Tags Class for Case Management Collection

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # Example of params input
        {
            'result_limit': 100,  # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary']  # Additional fields returned on the results
        }

    Args:
        initial_response: Initial data from ThreatConnect API.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the objects.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = UserGroupsModel(**kwargs)

    def __iter__(self) -> 'User':
        """Object iterator"""
        return self.iterate(base_class=UserGroup)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.USER_GROUPS.value

    @property
    def filter(self) -> 'FilterUserGroup':
        """Return instance of FilterArtifact Object."""
        return FilterUserGroup(self._session, self.tql)


class UserGroup(SecurityABC):
    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        # Might need to save id for submit request. Might be able to do a try catch though in parent.
        super().__init__(kwargs.pop('session', None))
        self._model = UserGroupModel(**kwargs)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.USER_GROUPS.value

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the Case."""

        return {'type': 'UserGroup', 'id': self.model.id, 'value': self.model.name}
