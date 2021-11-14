"""Tag / Tags Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tags.tag_filter import TagFilter
from tcex.api.tc.v3.tags.tag_model import TagModel, TagsModel


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

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = TagsModel(**kwargs)
        self.type_ = 'tags'

    def __iter__(self) -> 'Tag':
        """Iterate over CM objects."""
        return self.iterate(base_class=Tag)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TAGS.value

    @property
    def filter(self) -> 'TagFilter':
        """Return the type specific filter object."""
        return TagFilter(self.tql)


class Tag(ObjectABC):
    """Tags Object.

    Args:
        description (str, kwargs): A brief description of the Tag.
        name (str, kwargs): The **name** for the Tag.
        owner (str, kwargs): The name of the Owner of the Tag.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = TagModel(**kwargs)
        self._nested_filter = 'has_tag'
        self.type_ = 'Tag'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TAGS.value

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_
        if hasattr(self.model, 'type'):
            type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.name}
