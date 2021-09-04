"""Case Management Task"""
# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_task import FilterTask
from tcex.api.tc.v3.case_management.models.artifact_model import ArtifactModel
from tcex.api.tc.v3.case_management.models.note_model import NoteModel
from tcex.api.tc.v3.case_management.models.task_model import TaskModel, TasksModel
from tcex.api.tc.v3.case_management.tql import TQL


class Tasks(CaseManagementCollectionABC):
    """Tasks Class for Case Management Collection

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # Example of params input
        {
            'result_limit': 100,  # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary']  # Additional fields returned on the results
        }

    Args:
        initial_response: Initial data from ThreatConnect API.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the objects.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            kwargs.pop('session', None), kwargs.pop('tql_filter', None), kwargs.pop('params', None)
        )
        self._model = TasksModel(**kwargs)

    def __iter__(self) -> 'Task':
        """Object iterator"""
        return self.iterate(base_class=Task)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TASKS.value

    @property
    def filter(self) -> FilterTask:
        """Return instance of FilterTasks Object."""
        return FilterTask(self._session, self.tql)


class Task(CaseManagementABC):
    """Task object for Case Management."""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        super().__init__(kwargs.pop('session'))
        self._model = TaskModel(**kwargs)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TASKS.value

    @property
    def _base_filter(self):
        """Return the default filter."""
        return {
            'keyword': 'taskId',
            'operator': TQL.Operator.EQ,
            'value': self.model.id,
            'type_': TQL.Type.INTEGER,
        }

    @property
    def artifacts(self):
        # first-party
        from tcex.api.tc.v3.case_management.artifact import Artifacts

        yield from self._iterate_over_sublist(Artifacts)

    def add_artifact(self, **kwargs):
        """Add a artifact to the task"""
        self.model.artifacts.data.append(ArtifactModel(**kwargs))

    @property
    def notes(self):
        # first-party
        from tcex.api.tc.v3.case_management.note import Notes

        yield from self._iterate_over_sublist(Notes)

    def add_note(self, **kwargs):
        """Add a note to the task"""
        self.model.notes.data.append(NoteModel(**kwargs))

    @property
    def as_entity(self):
        """Return the entity representation of the Task."""
        return {'type': 'Task', 'value': self.model.name, 'id': self.model.id}
