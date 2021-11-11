"""UserGroup / UserGroups Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.user_groups.user_group_filter import UserGroupFilter
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel, UserGroupsModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator


class UserGroups(ObjectCollectionABC):
    """UserGroups Collection.

    # Example of params input
    {
        'result_limit': 100,  # Limit the retrieved results.
        'result_start': 10,  # Starting count used for pagination.
        'fields': ['caseId', 'summary']  # Select additional return fields.
    }

    Args:
        session (Session): Session object configured with TC API Auth.
        tql_filters (list): List of TQL filters.
        params (dict): Additional query params (see example above).
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = UserGroupsModel(**kwargs)
        self.type_ = 'user_groups'

    def __iter__(self) -> 'UserGroup':
        """Iterate over CM objects."""
        return self.iterate(base_class=UserGroup)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.USER_GROUPS.value

    @property
    def filter(self) -> 'UserGroupFilter':
        """Return the type specific filter object."""
        return UserGroupFilter(self.tql)


class UserGroup(ObjectABC):
    """UserGroups Object.

    Args:
        name (str, kwargs): The **name** for the User_Group.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = UserGroupModel(**kwargs)
        self.type_ = 'User Group'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.USER_GROUPS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'user_group_id',
            'operator': TqlOperator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_
        if hasattr(self.model, 'type'):
            type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}
