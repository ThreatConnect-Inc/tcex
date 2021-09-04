"""Note TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class NoteFilter(FilterABC):
    """Filter Object for Notes"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.NOTES.value

    def artifact_id(self, operator: Enum, artifact_id: int) -> None:
        """Filter Artifact ID based on **artifactId** keyword.

        Args:
            operator: The operator enum for the filter.
            artifact_id: The ID of the artifact this note is associated with.
        """
        self._tql.add_filter('artifactId', operator, artifact_id, TQL.Type.INTEGER)

    def author(self, operator: Enum, author: str) -> None:
        """Filter Author based on **author** keyword.

        Args:
            operator: The operator enum for the filter.
            author: The account login of the user who wrote the note.
        """
        self._tql.add_filter('author', operator, author, TQL.Type.STRING)

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case this note is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator: Enum, date_added: str) -> None:
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the note was written.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

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
    def has_task(self):
        """Return **FilterTask** for further filtering."""
        from tcex.api.tc.v3.tasks.filter import TaskFilter

        tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the case.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def last_modified(self, operator: Enum, last_modified: str) -> None:
        """Filter Last Modified based on **lastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            last_modified: The date the note was last modified.
        """
        self._tql.add_filter('lastModified', operator, last_modified, TQL.Type.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: Text of the first 100 characters of the note.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def task_id(self, operator: Enum, task_id: int) -> None:
        """Filter Task ID based on **taskId** keyword.

        Args:
            operator: The operator enum for the filter.
            task_id: The ID of the task this note is associated with.
        """
        self._tql.add_filter('taskId', operator, task_id, TQL.Type.INTEGER)

    def workflow_event_id(self, operator: Enum, workflow_event_id: int) -> None:
        """Filter Workflow Event ID based on **workflowEventId** keyword.

        Args:
            operator: The operator enum for the filter.
            workflow_event_id: The ID of the workflow event this note is associated with.
        """
        self._tql.add_filter('workflowEventId', operator, workflow_event_id, TQL.Type.INTEGER)
