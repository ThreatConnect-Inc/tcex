"""SystemRole / SystemRoles Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.system_roles.system_role_filter import SystemRoleFilter
from tcex.api.tc.v3.security.system_roles.system_role_model import SystemRoleModel, SystemRolesModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator


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

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = SystemRolesModel(**kwargs)
        self._type = 'system_roles'

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

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = SystemRoleModel(**kwargs)
        self.type_ = 'System Role'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.SYSTEM_ROLES.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'system_role_id',
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
