"""SystemRole / SystemRoles Object"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.system_roles.system_role_filter import SystemRoleFilter
from tcex.api.tc.v3.security.system_roles.system_role_model import SystemRoleModel, SystemRolesModel


class SystemRoles(ObjectCollectionABC):
    """SystemRoles Collection.

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
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = SystemRolesModel(**kwargs)
        self.type_ = 'system_roles'

    def __iter__(self) -> 'SystemRole':
        """Iterate over CM objects."""
        return self.iterate(base_class=SystemRole)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.SYSTEM_ROLES.value

    @property
    def filter(self) -> 'SystemRoleFilter':
        """Return the type specific filter object."""
        return SystemRoleFilter(self.tql)


class SystemRole(ObjectABC):
    """SystemRoles Object."""

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = SystemRoleModel(**kwargs)
        self._nested_field_name = 'systemRoles'
        self._nested_filter = 'has_system_role'
        self.type_ = 'System Role'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.SYSTEM_ROLES.value

    @property
    def model(self) -> 'SystemRoleModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['SystemRoleModel', dict]):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')
