"""Artifact Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class FilterArtifact(FilterABC):
    """Artifact Filter"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.ARTIFACTS.value

    def analytics_score(self, operator: Enum, analytics_score: int) -> None:
        """Filter Artifacts based on **analytics score** keyword.

        Args:
            operator: The operator enum for the filter.
            analytics_score: The score value to use for filtering.
        """
        self._tql.add_filter('analyticsScore', operator, analytics_score, TQL.Type.INT)

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Artifacts based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case associated with this artifact.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator: Enum, date_added: str):
        """Filter Artifact based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the artifact was written.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    # TODO: [low] cyclic import typing
    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_case import FilterCase

        cases = FilterCase(self._session, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    @property
    def has_group(self, id_: int) -> None:
        """Filter Artifact based on **group** association.

        Args:
            id_: The Id of the group.
        """
        self._tql.add_filter('hasGroup', TQL.Operator.EQ, id_, TQL.Type.INTEGER)

    @property
    def has_indicator(self, id_: int) -> None:
        """Filter Artifact based on **indicator** association.

        Args:
            id_: The Id of the indicator.
        """
        self._tql.add_filter('hasGroup', TQL.Operator.EQ, id_, TQL.Type.INTEGER)

    # TODO: [low] cyclic import typing
    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_note import FilterNote

        notes = FilterNote(self._session, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    # TODO: [low] cyclic import typing
    @property
    def has_task(self):
        """Return **FilterTask** for further filtering."""
        # first-party
        from tcex.api.tc.v3.case_management.filter_task import FilterTask

        tasks = FilterTask(self._session, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator: Enum, id_: int):
        """Filter Artifacts based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id_: The ID of the artifact.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def indicator_active(self, operator, active):
        """Filter Tasks based on **automated** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            active (bool): A flag indicating whether or not the artifact is active.
        """
        self._tql.add_filter('indicatorActive', operator, active, TQL.Type.BOOLEAN)

    def note_id(self, operator: Enum, note_id: int) -> None:
        """Filter Artifacts based on **noteId** keyword.

        Args:
            operator: The operator enum for the filter.
            note_id: The ID of the note associated with this artifact.
        """
        self._tql.add_filter('noteId', operator, note_id, TQL.Type.INTEGER)

    def source(self, operator: Enum, source: str) -> None:
        """Filter Artifacts based on **source** keyword.

        Args:
            operator: The operator enum for the filter.
            source: The source of the artifact.
        """
        self._tql.add_filter('source', operator, source, TQL.Type.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Artifacts based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary of the artifact.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def task_id(self, operator: Enum, task_id: int) -> None:
        """Filter Artifacts based on **taskId** keyword.

        Args:
            operator: The operator enum for the filter.
            task_id: The ID of the task associated with this artifact.
        """
        self._tql.add_filter('taskId', operator, task_id, TQL.Type.INTEGER)

    def type(self, operator: Enum, type_name: str):
        """Filter Artifacts based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The type name of the artifact.
        """
        self._tql.add_filter('typeName', operator, type_name, TQL.Type.STRING)

    def type_name(self, operator: Enum, type_name: str):
        """Filter Artifacts based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The type name of the artifact.
        """
        self._tql.add_filter('typeName', operator, type_name, TQL.Type.STRING)
