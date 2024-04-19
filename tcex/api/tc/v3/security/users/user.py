"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.users.user_filter import UserFilter
from tcex.api.tc.v3.security.users.user_model import UserModel, UsersModel


class User(ObjectABC):
    """Users Object."""

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: UserModel = UserModel(**kwargs)
        self._nested_field_name = 'users'
        self._nested_filter = 'has_user'
        self.type_ = 'User'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.USERS.value

    @property
    def model(self) -> UserModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | UserModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')


class Users(ObjectCollectionABC):
    """Users Collection.

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
        self._model = UsersModel(**kwargs)
        self.type_ = 'users'

    def __iter__(self) -> Iterator[User]:
        """Return CM objects."""
        return self.iterate(base_class=User)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.USERS.value

    @property
    def filter(self) -> UserFilter:
        """Return the type specific filter object."""
        return UserFilter(self.tql)
