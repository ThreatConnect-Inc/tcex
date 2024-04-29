"""TcEx Framework Module"""

# standard library
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.notes.note_model import NoteModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.workflow_events.workflow_event_filter import WorkflowEventFilter
from tcex.api.tc.v3.workflow_events.workflow_event_model import (
    WorkflowEventModel,
    WorkflowEventsModel,
)

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.notes.note import Note  # CIRCULAR-IMPORT


class WorkflowEvent(ObjectABC):
    """WorkflowEvents Object.

    Args:
        case_id (int, kwargs): The **case id** for the Workflow_Event.
        case_xid (str, kwargs): The **case xid** for the Workflow_Event.
        deleted_reason (str, kwargs): The reason for deleting the event (required input for DELETE
            operation only).
        event_date (str, kwargs): The time that the Event is logged.
        notes (Notes, kwargs): A list of Notes corresponding to the Event.
        summary (str, kwargs): The **summary** for the Workflow_Event.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: WorkflowEventModel = WorkflowEventModel(**kwargs)
        self._nested_field_name = 'workflowEvents'
        self._nested_filter = 'has_workflow_event'
        self.type_ = 'Workflow Event'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.WORKFLOW_EVENTS.value

    @property
    def model(self) -> WorkflowEventModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | WorkflowEventModel):
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

    @property
    def notes(self) -> Generator['Note', None, None]:
        """Yield Note from Notes."""
        # first-party
        from tcex.api.tc.v3.notes.note import Notes

        yield from self._iterate_over_sublist(Notes)  # type: ignore

    def stage_note(self, data: dict | ObjectABC | NoteModel):
        """Stage note on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = NoteModel(**data)

        if not isinstance(data, NoteModel):
            raise RuntimeError('Invalid type passed in to stage_note')
        data._staged = True
        self.model.notes.data.append(data)  # type: ignore


class WorkflowEvents(ObjectCollectionABC):
    """WorkflowEvents Collection.

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
        self._model = WorkflowEventsModel(**kwargs)
        self.type_ = 'workflow_events'

    def __iter__(self) -> Iterator[WorkflowEvent]:
        """Return CM objects."""
        return self.iterate(base_class=WorkflowEvent)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.WORKFLOW_EVENTS.value

    @property
    def filter(self) -> WorkflowEventFilter:
        """Return the type specific filter object."""
        return WorkflowEventFilter(self.tql)
