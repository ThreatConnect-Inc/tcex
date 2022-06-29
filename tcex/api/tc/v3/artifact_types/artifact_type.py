"""ArtifactType / ArtifactTypes Object"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifact_types.artifact_type_filter import ArtifactTypeFilter
from tcex.api.tc.v3.artifact_types.artifact_type_model import ArtifactTypeModel, ArtifactTypesModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class ArtifactTypes(ObjectCollectionABC):
    """ArtifactTypes Collection.

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
        self._model = ArtifactTypesModel(**kwargs)
        self.type_ = 'artifact_types'

    def __iter__(self) -> 'ArtifactType':
        """Iterate over CM objects."""
        return self.iterate(base_class=ArtifactType)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACT_TYPES.value

    @property
    def filter(self) -> 'ArtifactTypeFilter':
        """Return the type specific filter object."""
        return ArtifactTypeFilter(self.tql)


class ArtifactType(ObjectABC):
    """ArtifactTypes Object."""

    def __init__(self, **kwargs):
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = ArtifactTypeModel(**kwargs)
        self._nested_field_name = 'artifactTypes'
        self._nested_filter = 'has_artifact_type'
        self.type_ = 'Artifact Type'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ARTIFACT_TYPES.value

    @property
    def model(self) -> 'ArtifactTypeModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['ArtifactTypeModel', dict]):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_

        return {'type': type_, 'id': self.model.id, 'value': self.model.name}
