"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.intel_requirements.categories.category_filter import CategoryFilter
from tcex.api.tc.v3.intel_requirements.categories.category_model import (
    CategoriesModel,
    CategoryModel,
)
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class Category(ObjectABC):
    """Categories Object.

    Args:
        description (str, kwargs): The description of the subtype/category.
        name (str, kwargs): The details of the subtype/category.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: CategoryModel = CategoryModel(**kwargs)
        self._nested_field_name = 'categories'
        self._nested_filter = 'has_category'
        self.type_ = 'Category'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CATEGORIES.value

    @property
    def model(self) -> CategoryModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | CategoryModel):
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


class Categories(ObjectCollectionABC):
    """Categories Collection.

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
        self._model = CategoriesModel(**kwargs)
        self.type_ = 'categories'

    def __iter__(self) -> Iterator[Category]:
        """Return CM objects."""
        return self.iterate(base_class=Category)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.CATEGORIES.value

    @property
    def filter(self) -> CategoryFilter:
        """Return the type specific filter object."""
        return CategoryFilter(self.tql)
