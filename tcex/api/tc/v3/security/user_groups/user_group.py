"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.user_groups.user_group_filter import UserGroupFilter
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel, UserGroupsModel


class UserGroup(ObjectABC):
    """UserGroups Object."""

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: UserGroupModel = UserGroupModel(**kwargs)
        self._nested_field_name = 'userGroups'
        self._nested_filter = 'has_user_group'
        self.type_ = 'User Group'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.USER_GROUPS.value

    @property
    def model(self) -> UserGroupModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | UserGroupModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')


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

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = UserGroupsModel(**kwargs)
        self.type_ = 'user_groups'

    def __iter__(self) -> Iterator[UserGroup]:
        """Return CM objects."""
        return self.iterate(base_class=UserGroup)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.USER_GROUPS.value

    @property
    def filter(self) -> UserGroupFilter:
        """Return the type specific filter object."""
        return UserGroupFilter(self.tql)
