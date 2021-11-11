"""Note / Notes Object"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.notes.note_filter import NoteFilter
from tcex.api.tc.v3.notes.note_model import NoteModel, NotesModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tql.tql_operator import TqlOperator


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
        self._model = NoteModel(**kwargs)
        self.type_ = 'Note'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.NOTES.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'note_id',
            'operator': TqlOperator.EQ,
            'value': self.model.id,
            'type_': 'integer',
        }

    @property
    def as_entity(self) -> dict:
        """Return the entity representation of the object."""
        type_ = self.type_
        if hasattr(self.model, 'type'):
            type_ = self.model.type

        return {'type': type_, 'id': self.model.id, 'value': self.model.summary}
