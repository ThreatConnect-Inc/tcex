"""Note / Notes Object"""
# standard library
from typing import Union

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.notes.note_filter import NoteFilter
from tcex.api.tc.v3.notes.note_model import NoteModel, NotesModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC


class Notes(ObjectCollectionABC):
    """Notes Collection.

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
        self._model = NotesModel(**kwargs)
        self.type_ = 'notes'

    def __iter__(self) -> 'Note':
        """Iterate over CM objects."""
        return self.iterate(base_class=Note)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.NOTES.value

    @property
    def filter(self) -> 'NoteFilter':
        """Return the type specific filter object."""
        return NoteFilter(self.tql)


class Note(ObjectABC):
    """Notes Object.

    Args:
        artifact_id (int, kwargs): The ID of the Artifact on which to apply the Note.
        case_id (int, kwargs): The **case id** for the Note.
        case_xid (str, kwargs): The **case xid** for the Note.
        task_id (int, kwargs): The ID of the Task on which to apply the Note.
        task_xid (str, kwargs): The XID of the Task on which to apply the Note.
        text (str, kwargs): The **text** for the Note.
        workflow_event_id (int, kwargs): The ID of the Event on which to apply the Note.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model = NoteModel(**kwargs)
        self._nested_field_name = 'notes'
        self._nested_filter = 'has_note'
        self.type_ = 'Note'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.NOTES.value

    @property
    def model(self) -> 'NoteModel':
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: Union['NoteModel', dict]) -> None:
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

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}
