"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.owner_roles.owner_role_filter import OwnerRoleFilter
from tcex.api.tc.v3.security.owner_roles.owner_role_model import OwnerRoleModel, OwnerRolesModel


class OwnerRole(ObjectABC):
    """OwnerRoles Object."""

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: OwnerRoleModel = OwnerRoleModel(**kwargs)
        self._nested_field_name = 'ownerRoles'
        self._nested_filter = 'has_owner_role'
        self.type_ = 'Owner Role'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.OWNER_ROLES.value

    @property
    def model(self) -> OwnerRoleModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | OwnerRoleModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')


class OwnerRoles(ObjectCollectionABC):
    """OwnerRoles Collection.

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
        self._model = OwnerRolesModel(**kwargs)
        self.type_ = 'owner_roles'

    def __iter__(self) -> Iterator[OwnerRole]:
        """Return CM objects."""
        return self.iterate(base_class=OwnerRole)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.OWNER_ROLES.value

    @property
    def filter(self) -> OwnerRoleFilter:
        """Return the type specific filter object."""
        return OwnerRoleFilter(self.tql)
