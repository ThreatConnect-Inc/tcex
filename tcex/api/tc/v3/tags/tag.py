"""TcEx Framework Module"""

# standard library
import json
from collections.abc import Iterator

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tags.tag_filter import TagFilter
from tcex.api.tc.v3.tags.tag_model import TagModel, TagsModel


class Tag(ObjectABC):
    """Tags Object.

    Args:
        description (str, kwargs): A brief description of the Tag.
        name (str, kwargs): The **name** for the Tag.
        owner (str, kwargs): The name of the Owner of the Tag.
        security_coverage (object, kwargs): For ATT&CK-based tags, this is the security coverage
            level assigned to the tag.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: TagModel = TagModel(**kwargs)
        self._nested_field_name = 'tags'
        self._nested_filter = 'has_tag'
        self.type_ = 'Tag'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TAGS.value

    @property
    def model(self) -> TagModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | TagModel):
        """Create model using the provided data."""
        if isinstance(data, type(self.model)):
            # provided data is already a model, nothing required to change
            self._model = data
        elif isinstance(data, dict):
            # provided data is raw response, load the model
            self._model = type(self.model)(**data)
        else:
            raise RuntimeError(f'Invalid data type: {type(data)} provided.')

    def remove(self, params: dict | None = None):
        """Remove a nested object."""
        method = 'PUT'
        unique_id = self._calculate_unique_id()

        # validate an id is available
        self._validate_id(unique_id.get('value'), '')

        body = json.dumps(
            {
                self._nested_field_name: {
                    'data': [{unique_id.get('filter'): unique_id.get('value')}],
                    'mode': 'delete',
                }
            }
        )

        # get the unique id value for id, xid, summary, etc ...
        parent_api_endpoint = self._parent_data.get('api_endpoint')
        parent_unique_id = self._parent_data.get('unique_id')
        url = f'{parent_api_endpoint}/{parent_unique_id}'

        # validate parent an id is available
        self._validate_id(parent_unique_id, url)

        self._request(
            method=method,
            url=url,
            body=body,
            headers={'content-type': 'application/json'},
            params=params,
        )

        return self.request


class Tags(ObjectCollectionABC):
    """Tags Collection.

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
        self._model = TagsModel(**kwargs)
        self.type_ = 'tags'

    def __iter__(self) -> Iterator[Tag]:
        """Return CM objects."""
        return self.iterate(base_class=Tag)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TAGS.value

    @property
    def filter(self) -> TagFilter:
        """Return the type specific filter object."""
        return TagFilter(self.tql)
