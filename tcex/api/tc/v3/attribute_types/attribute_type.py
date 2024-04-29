"""TcEx Framework Module"""

# standard library
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.attribute_types.attribute_type_filter import AttributeTypeFilter
from tcex.api.tc.v3.attribute_types.attribute_type_model import (
    AttributeTypeModel,
    AttributeTypesModel,
)
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class AttributeType(ObjectABC):
    """AttributeTypes Object.

    Args:
        allow_markdown (bool, kwargs): Flag that enables markdown feature in the attribute value
            field.
        description (str, kwargs): The description of the attribute type.
        error_message (str, kwargs): The error message displayed.
        max_size (int, kwargs): The maximum size of the attribute value.
        name (str, kwargs): The name of the attribute type.
        validation_rule (object, kwargs): The validation rule that governs the attribute value.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: AttributeTypeModel = AttributeTypeModel(**kwargs)
        self._nested_field_name = 'attributeTypes'
        self._nested_filter = 'has_attribute_type'
        self.type_ = 'Attribute Type'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ATTRIBUTE_TYPES.value

    @property
    def model(self) -> AttributeTypeModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | AttributeTypeModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')


class AttributeTypes(ObjectCollectionABC):
    """AttributeTypes Collection.

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
        self._model = AttributeTypesModel(**kwargs)
        self.type_ = 'attribute_types'

    def __iter__(self) -> Iterator[AttributeType]:
        """Return CM objects."""
        return self.iterate(base_class=AttributeType)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.ATTRIBUTE_TYPES.value

    @property
    def filter(self) -> AttributeTypeFilter:
        """Return the type specific filter object."""
        return AttributeTypeFilter(self.tql)
