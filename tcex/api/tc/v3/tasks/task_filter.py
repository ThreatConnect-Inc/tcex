"""Task TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class TaskFilter(FilterABC):
    """Filter Object for Tasks"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TASKS.value

    def assigned_to_user_or_group(self, operator: Enum, assigned_to_user_or_group: str) -> None:
        """Filter Assigned To User or Group based on **assignedToUserOrGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            assigned_to_user_or_group: A value of User, Group, or None depending on the assignee.
        """
        self._tql.add_filter(
            'assignedToUserOrGroup', operator, assigned_to_user_or_group, TqlType.STRING
        )

    def assignee_name(self, operator: Enum, assignee_name: str) -> None:
        """Filter Assignee Name based on **assigneeName** keyword.

        Args:
            operator: The operator enum for the filter.
            assignee_name: The user or group name assigned to the Task.
        """
        self._tql.add_filter('assigneeName', operator, assignee_name, TqlType.STRING)

    def automated(self, operator: Enum, automated: bool) -> None:
        """Filter Automated based on **automated** keyword.

        Args:
            operator: The operator enum for the filter.
            automated: A flag indicating whether or not the task is automated.
        """
        self._tql.add_filter('automated', operator, automated, TqlType.BOOLEAN)

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case this Task is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TqlType.INTEGER)

    def case_id_as_string(self, operator: Enum, case_id_as_string: str) -> None:
        """Filter CaseID As String based on **caseIdAsString** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id_as_string: The ID of the case as a String.
        """
        self._tql.add_filter('caseIdAsString', operator, case_id_as_string, TqlType.STRING)

    def case_severity(self, operator: Enum, case_severity: str) -> None:
        """Filter Case Severity based on **caseSeverity** keyword.

        Args:
            operator: The operator enum for the filter.
            case_severity: The severity of the case associated with the task.
        """
        self._tql.add_filter('caseSeverity', operator, case_severity, TqlType.STRING)

    def completed_by(self, operator: Enum, completed_by: str) -> None:
        """Filter Completed By based on **completedBy** keyword.

        Args:
            operator: The operator enum for the filter.
            completed_by: The account login of the user who completed the task.
        """
        self._tql.add_filter('completedBy', operator, completed_by, TqlType.STRING)

    def completed_date(self, operator: Enum, completed_date: str) -> None:
        """Filter Completed Date based on **completedDate** keyword.

        Args:
            operator: The operator enum for the filter.
            completed_date: The completion date for the task.
        """
        completed_date = self.utils.any_to_datetime(completed_date).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('completedDate', operator, completed_date, TqlType.STRING)

    def description(self, operator: Enum, description: str) -> None:
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the task.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def due_date(self, operator: Enum, due_date: str) -> None:
        """Filter Due Date based on **dueDate** keyword.

        Args:
            operator: The operator enum for the filter.
            due_date: The due date for the task.
        """
        due_date = self.utils.any_to_datetime(due_date).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('dueDate', operator, due_date, TqlType.STRING)

    @property
    def has_artifact(self):
        """Return **ArtifactFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter

        artifacts = ArtifactFilter(Tql())
        self._tql.add_filter('hasArtifact', TqlOperator.EQ, artifacts, TqlType.SUB_QUERY)
        return artifacts

    @property
    def has_case(self):
        """Return **CaseFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.cases.case_filter import CaseFilter

        cases = CaseFilter(Tql())
        self._tql.add_filter('hasCase', TqlOperator.EQ, cases, TqlType.SUB_QUERY)
        return cases

    @property
    def has_note(self):
        """Return **NoteFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.notes.note_filter import NoteFilter

        notes = NoteFilter(Tql())
        self._tql.add_filter('hasNote', TqlOperator.EQ, notes, TqlType.SUB_QUERY)
        return notes

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the task.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the task.
        """
        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def required(self, operator: Enum, required: bool) -> None:
        """Filter Required based on **required** keyword.

        Args:
            operator: The operator enum for the filter.
            required: Flag indicating whether or not the task is required.
        """
        self._tql.add_filter('required', operator, required, TqlType.BOOLEAN)

    def status(self, operator: Enum, status: str) -> None:
        """Filter Status based on **status** keyword.

        Args:
            operator: The operator enum for the filter.
            status: The status of the task.
        """
        self._tql.add_filter('status', operator, status, TqlType.STRING)

    def target_id(self, operator: Enum, target_id: int) -> None:
        """Filter Assignee based on **targetId** keyword.

        Args:
            operator: The operator enum for the filter.
            target_id: The assigned user or group ID for the task.
        """
        self._tql.add_filter('targetId', operator, target_id, TqlType.INTEGER)

    def target_type(self, operator: Enum, target_type: str) -> None:
        """Filter Target Type based on **targetType** keyword.

        Args:
            operator: The operator enum for the filter.
            target_type: The target type for this task (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TqlType.STRING)

    def workflow_phase(self, operator: Enum, workflow_phase: int) -> None:
        """Filter Workflow Phase based on **workflowPhase** keyword.

        Args:
            operator: The operator enum for the filter.
            workflow_phase: The workflow phase of the task.
        """
        self._tql.add_filter('workflowPhase', operator, workflow_phase, TqlType.INTEGER)

    def workflow_step(self, operator: Enum, workflow_step: int) -> None:
        """Filter Workflow Step based on **workflowStep** keyword.

        Args:
            operator: The operator enum for the filter.
            workflow_step: The workflow step of the task.
        """
        self._tql.add_filter('workflowStep', operator, workflow_step, TqlType.INTEGER)

    def xid(self, operator: Enum, xid: str) -> None:
        """Filter XID based on **xid** keyword.

        Args:
            operator: The operator enum for the filter.
            xid: The XID of the task.
        """
        self._tql.add_filter('xid', operator, xid, TqlType.STRING)
