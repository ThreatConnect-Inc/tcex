"""Case Management Workflow Event"""

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.case_management_abc import CaseManagementABC
from tcex.api.tc.v3.case_management.case_management_collection_abc import (
    CaseManagementCollectionABC,
)
from tcex.api.tc.v3.case_management.filter_workflow_event import FilterWorkflowEvent
from tcex.api.tc.v3.case_management.models.note_model import NoteModel
from tcex.api.tc.v3.case_management.models.workflow_event_model import (
    WorkflowEventModel,
    WorkflowEventsModel,
)
from tcex.api.tc.v3.case_management.tql import TQL


class WorkflowEvents(CaseManagementCollectionABC):
    """Case Management Workflow Event

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
        self._model = WorkflowEventsModel(**kwargs)

    def __iter__(self) -> 'WorkflowEvent':
        """Object iterator"""
        return self.iterate(base_class=WorkflowEvent)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.WORKFLOW_EVENTS.value

    @property
    def filter(self):
        """Return instance of FilterWorkflowEvent Object."""
        return FilterWorkflowEvent(self._session, self.tql)


class WorkflowEvent(CaseManagementABC):
    """WorkflowEvent object for Case Management."""

    def __init__(self, **kwargs) -> None:
        """Initialize Class properties"""
        super().__init__(kwargs.pop('session'))
        self._model = WorkflowEventModel(**kwargs)

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.WORKFLOW_EVENTS.value

    @property
    def _base_filter(self) -> dict:
        """Return the default filter."""
        return {
            'keyword': 'workflowEventId',
            'operator': TQL.Operator.EQ,
            'value': self.model.id,
            'type_': TQL.Type.INTEGER,
        }

    @property
    def notes(self):
        # first-party
        from tcex.api.tc.v3.case_management.note import Notes

        yield from self._iterate_over_sublist(Notes)

    def add_note(self, **kwargs) -> None:
        """Add a Note to a Workflow Event."""
        self.model.notes.data.append(NoteModel(**kwargs))

    @property
    def as_entity(self):
        """Return the entity representation of the Workflow Event."""
        return {'type': 'Workflow Event', 'value': self.model.summary, 'id': self.model.id}
