"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.intel_requirements.subtypes.subtype_filter import SubtypeFilter
from tcex.api.tc.v3.intel_requirements.subtypes.subtype_model import SubtypeModel, SubtypesModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class Subtype(ObjectABC):
    """Subtypes Object.

    Args:
        description (str, kwargs): The description of the subtype/category.
        name (str, kwargs): The details of the subtype/category.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: SubtypeModel = SubtypeModel(**kwargs)
        self._nested_field_name = 'subtypes'
        self._nested_filter = 'has_subtype'
        self.type_ = 'Subtype'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.SUBTYPES.value

    @property
    def model(self) -> SubtypeModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | SubtypeModel):
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


class Subtypes(ObjectCollectionABC):
    """Subtypes Collection.

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
        self._model = SubtypesModel(**kwargs)
        self.type_ = 'subtypes'

    def __iter__(self) -> Iterator[Subtype]:
        """Return CM objects."""
        return self.iterate(base_class=Subtype)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.SUBTYPES.value

    @property
    def filter(self) -> SubtypeFilter:
        """Return the type specific filter object."""
        return SubtypeFilter(self.tql)
