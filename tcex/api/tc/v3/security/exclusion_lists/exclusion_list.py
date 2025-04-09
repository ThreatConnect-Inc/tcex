"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.exclusion_lists.exclusion_list_filter import ExclusionListFilter
from tcex.api.tc.v3.security.exclusion_lists.exclusion_list_model import (
    ExclusionListModel,
    ExclusionListsModel,
)


class ExclusionList(ObjectABC):
    """ExclusionLists Object.

    Args:
        active (bool, kwargs): Whether the rule is active or not.
        fixed_values (object, kwargs): A list of exclusions represent fixed values.
        managed (bool, kwargs): Whether the rule is managed by the system.
        name (str, kwargs): The name of the rule.
        owner (str, kwargs): The name of the Owner of the Exclusion List.
        owner_id (int, kwargs): The ID of the owner of this exclusion list.
        variable_values (object, kwargs): A list of exclusions serve as wildcards.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: ExclusionListModel = ExclusionListModel(**kwargs)
        self._nested_field_name = 'exclusionLists'
        self._nested_filter = 'has_exclusion_list'
        self.type_ = 'Exclusion List'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.EXCLUSION_LISTS.value

    @property
    def model(self) -> ExclusionListModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | ExclusionListModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            ex_msg = f'Invalid data type: {type(data)} provided.'
            raise RuntimeError(ex_msg)  # noqa: TRY004


class ExclusionLists(ObjectCollectionABC):
    """ExclusionLists Collection.

    # Example of params input
    {
        "result_limit": 100,  # Limit the retrieved results.
        "result_start": 10,  # Starting count used for pagination.
        "fields": ["caseId", "summary"]  # Select additional return fields.
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
        self._model = ExclusionListsModel(**kwargs)
        self.type_ = 'exclusion_lists'

    def __iter__(self) -> Iterator[ExclusionList]:
        """Return CM objects."""
        return self.iterate(base_class=ExclusionList)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.EXCLUSION_LISTS.value

    @property
    def filter(self) -> ExclusionListFilter:
        """Return the type specific filter object."""
        return ExclusionListFilter(self.tql)
