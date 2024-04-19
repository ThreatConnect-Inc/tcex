"""TcEx Framework Module"""

# standard library
from collections.abc import Generator, Iterator
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.artifacts.artifact_model import ArtifactModel
from tcex.api.tc.v3.notes.note_model import NoteModel
from tcex.api.tc.v3.object_abc import ObjectABC
from tcex.api.tc.v3.object_collection_abc import ObjectCollectionABC
from tcex.api.tc.v3.security.user_groups.user_group_model import UserGroupModel
from tcex.api.tc.v3.security.users.user_model import UserModel
from tcex.api.tc.v3.tasks.task_filter import TaskFilter
from tcex.api.tc.v3.tasks.task_model import TaskModel, TasksModel

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.api.tc.v3.artifacts.artifact import Artifact  # CIRCULAR-IMPORT
    from tcex.api.tc.v3.notes.note import Note  # CIRCULAR-IMPORT


class Task(ObjectABC):
    """Tasks Object.

    Args:
        artifacts (Artifacts, kwargs): A list of Artifacts corresponding to the Task.
        assignee (Assignee, kwargs): The user or group Assignee object for the Task.
        case_id (int, kwargs): The **case id** for the Task.
        case_xid (str, kwargs): The **case xid** for the Task.
        completed_date (str, kwargs): The completion date of the Task.
        dependent_on_id (int, kwargs): The ID of another Task that this Task is dependent upon.
        description (str, kwargs): The **description** for the Task.
        due_date (str, kwargs): The due date of the Task.
        duration_type (str, kwargs): The **duration type** for the Task.
        name (str, kwargs): The **name** for the Task.
        notes (Notes, kwargs): A list of Notes corresponding to the Task.
        required (bool, kwargs): Flag indicating whether or not the task is required.
        status (str, kwargs): The **status** for the Task.
        workflow_phase (int, kwargs): The phase of the workflow.
        workflow_step (int, kwargs): The step of the workflow.
        xid (str, kwargs): The **xid** for the Task.
    """

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(kwargs.pop('session', None))

        # properties
        self._model: TaskModel = TaskModel(**kwargs)
        self._nested_field_name = 'tasks'
        self._nested_filter = 'has_task'
        self.type_ = 'Task'

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TASKS.value

    @property
    def model(self) -> TaskModel:
        """Return the model data."""
        return self._model

    @model.setter
    def model(self, data: dict | TaskModel):
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

    @property
    def artifacts(self) -> Generator['Artifact', None, None]:
        """Yield Artifact from Artifacts."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact import Artifacts

        yield from self._iterate_over_sublist(Artifacts)  # type: ignore

    @property
    def notes(self) -> Generator['Note', None, None]:
        """Yield Note from Notes."""
        # first-party
        from tcex.api.tc.v3.notes.note import Notes

        yield from self._iterate_over_sublist(Notes)  # type: ignore

    def stage_artifact(self, data: dict | ObjectABC | ArtifactModel):
        """Stage artifact on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif isinstance(data, dict):
            data = ArtifactModel(**data)

        if not isinstance(data, ArtifactModel):
            raise RuntimeError('Invalid type passed in to stage_artifact')
        data._staged = True
        self.model.artifacts.data.append(data)  # type: ignore

    # pylint: disable=redefined-builtin
    def stage_assignee(self, type: str, data: dict | ObjectABC | UserModel | UserGroupModel):
        """Stage artifact on the object."""
        if isinstance(data, ObjectABC):
            data = data.model  # type: ignore
        elif type.lower() == 'user' and isinstance(data, dict):
            data = UserModel(**data)
        elif type.lower() == 'group' and isinstance(data, dict):
            data = UserGroupModel(**data)

        if not isinstance(data, UserModel | UserGroupModel):
            raise RuntimeError('Invalid type passed in to stage_assignee')
        data._staged = True
        self.model.assignee._staged = True
        self.model.assignee.type = type
        self.model.assignee.data = data  # type: ignore

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

    def __init__(self, **kwargs):
        """Initialize instance properties."""
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = TasksModel(**kwargs)
        self.type_ = 'tasks'

    def __iter__(self) -> Iterator[Task]:
        """Return CM objects."""
        return self.iterate(base_class=Task)  # type: ignore

    @property
    def _api_endpoint(self) -> str:
        """Return the type specific API endpoint."""
        return ApiEndpoints.TASKS.value

    @property
    def filter(self) -> TaskFilter:
        """Return the type specific filter object."""
        return TaskFilter(self.tql)
