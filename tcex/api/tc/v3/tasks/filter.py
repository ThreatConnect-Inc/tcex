"""Task TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class TaskFilter(FilterABC):
    """Filter Object for Tasks"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TASKS.value

    def automated(self, operator: Enum, automated: bool) -> None:
        """Filter Automated based on **automated** keyword.

        Args:
            operator: The operator enum for the filter.
            automated: A flag indicating whether or not the task is automated.
        """
        self._tql.add_filter('automated', operator, automated, TQL.Type.BOOLEAN)

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case this Task is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def case_severity(self, operator: Enum, case_severity: str) -> None:
        """Filter Case Severity based on **caseSeverity** keyword.

        Args:
            operator: The operator enum for the filter.
            case_severity: The severity of the case associated with the task.
        """
        self._tql.add_filter('caseSeverity', operator, case_severity, TQL.Type.STRING)

    def completed_by(self, operator: Enum, completed_by: str) -> None:
        """Filter Completed By based on **completedBy** keyword.

        Args:
            operator: The operator enum for the filter.
            completed_by: The account login of the user who completed the task.
        """
        self._tql.add_filter('completedBy', operator, completed_by, TQL.Type.STRING)

    def completed_date(self, operator: Enum, completed_date: str) -> None:
        """Filter Completed Date based on **completedDate** keyword.

        Args:
            operator: The operator enum for the filter.
            completed_date: The completion date for the task.
        """
        self._tql.add_filter('completedDate', operator, completed_date, TQL.Type.STRING)

    def description(self, operator: Enum, description: str) -> None:
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the task.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    def due_date(self, operator: Enum, due_date: str) -> None:
        """Filter Due Date based on **dueDate** keyword.

        Args:
            operator: The operator enum for the filter.
            due_date: The due date for the task.
        """
        self._tql.add_filter('dueDate', operator, due_date, TQL.Type.STRING)

    @property
    def has_artifact(self):
        """Return **FilterArtifacts** for further filtering."""
        from tcex.api.tc.v3.artifacts.filter import ArtifactFilter

        artifacts = FilterArtifacts(ApiEndpoints.ARTIFACTS, self._tcex, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from tcex.api.tc.v3.cases.filter import CaseFilter

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        from tcex.api.tc.v3.notes.filter import NoteFilter

        notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the task.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the task.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def required(self, operator: Enum, required: bool) -> None:
        """Filter Required based on **required** keyword.

        Args:
            operator: The operator enum for the filter.
            required: Flag indicating whether or not the task is required.
        """
        self._tql.add_filter('required', operator, required, TQL.Type.BOOLEAN)

    def status(self, operator: Enum, status: str) -> None:
        """Filter Status based on **status** keyword.

        Args:
            operator: The operator enum for the filter.
            status: The status of the task.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def target_id(self, operator: Enum, target_id: int) -> None:
        """Filter Assignee based on **targetId** keyword.

        Args:
            operator: The operator enum for the filter.
            target_id: The assigned user or group ID for the task.
        """
        self._tql.add_filter('targetId', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator: Enum, target_type: str) -> None:
        """Filter Target Type based on **targetType** keyword.

        Args:
            operator: The operator enum for the filter.
            target_type: The target type for this task (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TQL.Type.STRING)

    def workflow_phase(self, operator: Enum, workflow_phase: int) -> None:
        """Filter Workflow Phase based on **workflowPhase** keyword.

        Args:
            operator: The operator enum for the filter.
            workflow_phase: The workflow phase of the task.
        """
        self._tql.add_filter('workflowPhase', operator, workflow_phase, TQL.Type.INTEGER)

    def workflow_step(self, operator: Enum, workflow_step: int) -> None:
        """Filter Workflow Step based on **workflowStep** keyword.

        Args:
            operator: The operator enum for the filter.
            workflow_step: The workflow step of the task.
        """
        self._tql.add_filter('workflowStep', operator, workflow_step, TQL.Type.INTEGER)

    def xid(self, operator: Enum, xid: str) -> None:
        """Filter XID based on **xid** keyword.

        Args:
            operator: The operator enum for the filter.
            xid: The XID of the task.
        """
        self._tql.add_filter('xid', operator, xid, TQL.Type.STRING)
