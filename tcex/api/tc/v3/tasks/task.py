"""Task / Tasks Object"""
# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.notes.note_model import NoteModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.tasks.task_filter import TaskFilter
from tcex.api.tc.v3.tasks.task_model import TaskModel, TasksModel
from tcex.api.tc.v3.tql.tql_operator import TqlOperator

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact
    from tcex.api.tc.v3.notes.note import Note


class Tasks(ObjectCollectionABC):
    """Tasks Collection.

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
        self._model = TasksModel(**kwargs)
        self._type = 'tasks'

    def __iter__(self) -> 'Task':
        """Iterate over CM objects."""
        return self.iterate(base_class=Task)

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TASKS.value

    @property
    def filter(self) -> 'TaskFilter':
        """Return the type specific filter object."""
        return TaskFilter(self.tql)


class Task(ObjectABC):
    """Tasks Object.

    Args:
        artifacts (Artifacts, kwargs): A list of Artifacts corresponding to the Task.
        assignee (None, kwargs): The user or group Assignee object for the Task.
        case_id (int, kwargs): The **case id** for the Task.
        case_xid (str, kwargs): The **case xid** for the Task.
        completed_date (str, kwargs): The completion date of the Task.
        dependent_on_id (int, kwargs): The ID of another Task that this Task is dependent upon.
        description (str, kwargs): The **description** for the Task.
        due_date (str, kwargs): The due date of the Task.
        name (str, kwargs): The **name** for the Task.
        notes (Notes, kwargs): A list of Notes corresponding to the Task.
        required (bool, kwargs): Flag indicating whether or not the task is required.
        status (str, kwargs): The **status** for the Task.
        workflow_phase (int, kwargs): The phase of the workflow.
        workflow_step (int, kwargs): The step of the workflow.
        xid (str, kwargs): The **xid** for the Task.
    """

    def __init__(self, **kwargs) -> None:
        """Initialize class properties."""
        super().__init__(kwargs.pop('session', None))
        self._model = TaskModel(**kwargs)
        self.type_ = 'Task'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TASKS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'task_id',
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

        return {'type': type_, 'id': self.model.id, 'value': self.model.name}

    def add_artifact(self, **kwargs) -> None:
        """Add artifact to the object.

        Args:
            derived_link (bool, kwargs): Flag to specify if this artifact should be used for
                potentially associated cases or not.
            field_name (str, kwargs): The field name for the artifact.
            file_data (str, kwargs): Base64 encoded file attachment required only for certain
                artifact types.
            source (str, kwargs): The **source** for the Artifact.
            summary (str, kwargs): The **summary** for the Artifact.
        """
        self.model.artifacts.data.append(ArtifactModel(**kwargs))

    def add_note(self, **kwargs) -> None:
        """Add note to the object.

        Args:
            text (str, kwargs): The **text** for the Note.
        """
        self.model.notes.data.append(NoteModel(**kwargs))

    @property
    def artifacts(self) -> 'Artifact':
        """Yield Artifact from Artifacts."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact import Artifacts

        yield from self._iterate_over_sublist(Artifacts)

    @property
    def notes(self) -> 'Note':
        """Yield Note from Notes."""
        # first-party
        from tcex.api.tc.v3.notes.note import Notes

        yield from self._iterate_over_sublist(Notes)
