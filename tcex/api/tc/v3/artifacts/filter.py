"""Artifact TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class ArtifactFilter(FilterABC):
    """Filter Object for Artifacts"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.ARTIFACTS.value

    def analytics_score(self, operator: Enum, analytics_score: int) -> None:
        """Filter Analytics Score based on **analyticsScore** keyword.

        Args:
            operator: The operator enum for the filter.
            analytics_score: The intel score of the artifact.
        """
        self._tql.add_filter('analyticsScore', operator, analytics_score, TQL.Type.INTEGER)

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case associated with this artifact.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator: Enum, date_added: str) -> None:
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the artifact was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from tcex.api.tc.v3.cases.filter import CaseFilter

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    def has_group(self, operator: Enum, has_group: int) -> None:
        """Filter Associated Bucket based on **hasGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            has_group: A nested query for association to other buckets.
        """
        self._tql.add_filter('hasGroup', operator, has_group, TQL.Type.INTEGER)

    def has_indicator(self, operator: Enum, has_indicator: int) -> None:
        """Filter Associated Indicator based on **hasIndicator** keyword.

        Args:
            operator: The operator enum for the filter.
            has_indicator: A nested query for association to other indicators.
        """
        self._tql.add_filter('hasIndicator', operator, has_indicator, TQL.Type.INTEGER)

    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        from tcex.api.tc.v3.notes.filter import NoteFilter

        notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

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
            id: The ID of the artifact.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def indicator_active(self, operator: Enum, indicator_active: bool) -> None:
        """Filter Active Status based on **indicatorActive** keyword.

        Args:
            operator: The operator enum for the filter.
            indicator_active: A flag indicating whether or not the artifact is active.
        """
        self._tql.add_filter('indicatorActive', operator, indicator_active, TQL.Type.BOOLEAN)

    def note_id(self, operator: Enum, note_id: int) -> None:
        """Filter Note ID based on **noteId** keyword.

        Args:
            operator: The operator enum for the filter.
            note_id: The ID of the note associated with this artifact.
        """
        self._tql.add_filter('noteId', operator, note_id, TQL.Type.INTEGER)

    def source(self, operator: Enum, source: str) -> None:
        """Filter Source based on **source** keyword.

        Args:
            operator: The operator enum for the filter.
            source: The source of the artifact.
        """
        self._tql.add_filter('source', operator, source, TQL.Type.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary of the artifact.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def task_id(self, operator: Enum, task_id: int) -> None:
        """Filter Task ID based on **taskId** keyword.

        Args:
            operator: The operator enum for the filter.
            task_id: The ID of the task associated with this artifact.
        """
        self._tql.add_filter('taskId', operator, task_id, TQL.Type.INTEGER)

    def type(self, operator: Enum, type: str) -> None:  # pylint: disable=redefined-builtin
        """Filter typeName based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The type name of the artifact.
        """
        self._tql.add_filter('type', operator, type, TQL.Type.STRING)

    def type_name(self, operator: Enum, type_name: str) -> None:
        """Filter typeName based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The type name of the artifact.
        """
        self._tql.add_filter('typeName', operator, type_name, TQL.Type.STRING)
