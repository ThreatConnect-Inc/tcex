"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.intel_requirements.results.result_filter import ResultFilter
from tcex.api.tc.v3.intel_requirements.results.result_model import ResultModel, ResultsModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class Result(ObjectABC):
    """Results Object.

    Args:
        archived (bool, kwargs): Has the result been archived?
        associated (bool, kwargs): Has the result been associated to an entity within Threatconnect?
        false_positive (bool, kwargs): Is the result declared false positive?
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: ResultModel = ResultModel(**kwargs)
        self._nested_field_name = 'results'
        self._nested_filter = 'has_result'
        self.type_ = 'Result'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.RESULTS.value

    @property
    def model(self) -> ResultModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | ResultModel):
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


class Results(ObjectCollectionABC):
    """Results Collection.

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
        self._model = ResultsModel(**kwargs)
        self.type_ = 'results'

    def __iter__(self) -> Iterator[Result]:
        """Return CM objects."""
        return self.iterate(base_class=Result)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.RESULTS.value

    @property
    def filter(self) -> ResultFilter:
        """Return the type specific filter object."""
        return ResultFilter(self.tql)
