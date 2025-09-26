"""TcEx Framework Module"""

from collections.abc import Iterator

from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.notes.note_filter import NoteFilter
from tcex.api.tc.v3.notes.note_model import NoteModel, NotesModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class Note(ObjectABC):
    """Notes Object."""

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: NoteModel = NoteModel(**kwargs)
        self._nested_field_name = 'notes'
        self._nested_filter = 'has_note'
        self.type_ = 'Note'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.NOTES.value

    @property
    def model(self) -> NoteModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | NoteModel):
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

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}


class Notes(ObjectCollectionABC):
    """Notes Collection.

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
        self._model = NotesModel(**kwargs)
        self.type_ = 'notes'

    def __iter__(self) -> Iterator[Note]:
        """Return CM objects."""
        return self.iterate(base_class=Note)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.NOTES.value

    @property
    def filter(self) -> NoteFilter:
        """Return the type specific filter object."""
        return NoteFilter(self.tql)
