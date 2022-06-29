"""Note TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class NoteFilter(FilterABC):
    """Filter Object for Notes"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.NOTES.value

    def artifact_id(self, operator: Enum, artifact_id: int):
        """Filter Artifact ID based on **artifactId** keyword.

        Args:
            operator: The operator enum for the filter.
            artifact_id: The ID of the artifact this note is associated with.
        """
        self._tql.add_filter('artifactId', operator, artifact_id, TqlType.INTEGER)

    def author(self, operator: Enum, author: str):
        """Filter Author based on **author** keyword.

        Args:
            operator: The operator enum for the filter.
            author: The account login of the user who wrote the note.
        """
        self._tql.add_filter('author', operator, author, TqlType.STRING)

    def case_id(self, operator: Enum, case_id: int):
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case this note is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TqlType.INTEGER)

    def date_added(self, operator: Enum, date_added: str):
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the note was written.
        """
        date_added = self.utils.any_to_datetime(date_added).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

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
    def has_task(self):
        """Return **TaskFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tasks.task_filter import TaskFilter

        tasks = TaskFilter(Tql())
        self._tql.add_filter('hasTask', TqlOperator.EQ, tasks, TqlType.SUB_QUERY)
        return tasks

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the case.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def last_modified(self, operator: Enum, last_modified: str):
        """Filter Last Modified based on **lastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            last_modified: The date the note was last modified.
        """
        last_modified = self.utils.any_to_datetime(last_modified).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('lastModified', operator, last_modified, TqlType.STRING)

    def summary(self, operator: Enum, summary: str):
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: Text of the first 100 characters of the note.
        """
        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def task_id(self, operator: Enum, task_id: int):
        """Filter Task ID based on **taskId** keyword.

        Args:
            operator: The operator enum for the filter.
            task_id: The ID of the task this note is associated with.
        """
        self._tql.add_filter('taskId', operator, task_id, TqlType.INTEGER)

    def workflow_event_id(self, operator: Enum, workflow_event_id: int):
        """Filter Workflow Event ID based on **workflowEventId** keyword.

        Args:
            operator: The operator enum for the filter.
            workflow_event_id: The ID of the workflow event this note is associated with.
        """
        self._tql.add_filter('workflowEventId', operator, workflow_event_id, TqlType.INTEGER)
