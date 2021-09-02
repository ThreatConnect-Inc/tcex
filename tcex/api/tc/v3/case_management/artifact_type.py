"""ThreatConnect Case Management Artifact Type"""
# standard library
from typing import Dict

# first-party
from tcex.api.tc.v3.case_management.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_artifact_type import FilterArtifactType
from tcex.api.tc.v3.case_management.models.artifact_type_model import (
    ArtifactTypeData,
    ArtifactTypeModel,
)
from tcex.api.tc.v3.case_management.tql import TQL


class ArtifactTypes(CaseManagementCollectionABC):
    """Artifact Type collections object

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
        session: List of TQL filters.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the objects.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = ArtifactTypeData(**kwargs)

    def __iter__(self) -> 'ArtifactType':
        """Iterate over CM objects."""
        return self.iterate(base_class=ArtifactType)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACT_TYPES.value

    @property
    def filter(self) -> 'FilterArtifactType':
        """Return the type specific filter object."""
        return FilterArtifactType(self._session, self.tql)


class ArtifactType(CaseManagementABC):
    """Artifact Type individual object."""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        # TODO: [high] @bpurdy - Might need to save id for submit request.
        #       Might be able to do a try catch though in parent.
        super().__init__(kwargs.pop('session', None))
        self._model = ArtifactTypeModel(**kwargs)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACT_TYPES.value

    def _base_filter(self) -> dict:
        return {
            'keyword': 'artifacttypeid',
            'operator': TQL.Operator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def as_entity(self) -> Dict[str, str]:
        """Return the entity representation of the object."""
        return {'type': 'Artifact Type', 'value': self.model.name, 'id': self.model.id}
