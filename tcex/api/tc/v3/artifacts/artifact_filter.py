"""TcEx Framework Module"""

# standard library
from datetime import datetime
from enum import Enum

# third-party
from arrow import Arrow

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class ArtifactFilter(FilterABC):
    """Filter Object for Artifacts"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.ARTIFACTS.value

    def analytics_score(self, operator: Enum, analytics_score: int | list):
        """Filter Analytics Score based on **analyticsScore** keyword.

        Args:
            operator: The operator enum for the filter.
            analytics_score: The intel score of the artifact.
        """
        if isinstance(analytics_score, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('analyticsScore', operator, analytics_score, TqlType.INTEGER)

    def case_id(self, operator: Enum, case_id: int | list):
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case associated with this artifact.
        """
        if isinstance(case_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('caseId', operator, case_id, TqlType.INTEGER)

    def date_added(self, operator: Enum, date_added: Arrow | datetime | int | str):
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the artifact was added to the system.
        """
        date_added = self.util.any_to_datetime(date_added).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    @property
    def has_case(self):
        """Return **CaseFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.cases.case_filter import CaseFilter

        cases = CaseFilter(Tql())
        self._tql.add_filter('hasCase', TqlOperator.EQ, cases, TqlType.SUB_QUERY)
        return cases

    @property
    def has_group(self):
        """Return **GroupFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.groups.group_filter import GroupFilter

        groups = GroupFilter(Tql())
        self._tql.add_filter('hasGroup', TqlOperator.EQ, groups, TqlType.SUB_QUERY)
        return groups

    @property
    def has_indicator(self):
        """Return **IndicatorFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter

        indicators = IndicatorFilter(Tql())
        self._tql.add_filter('hasIndicator', TqlOperator.EQ, indicators, TqlType.SUB_QUERY)
        return indicators

    @property
    def has_note(self):
        """Return **NoteFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.notes.note_filter import NoteFilter

        notes = NoteFilter(Tql())
        self._tql.add_filter('hasNote', TqlOperator.EQ, notes, TqlType.SUB_QUERY)
        return notes

    @property
    def has_task(self):
        """Return **TaskFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tasks.task_filter import TaskFilter

        tasks = TaskFilter(Tql())
        self._tql.add_filter('hasTask', TqlOperator.EQ, tasks, TqlType.SUB_QUERY)
        return tasks

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the artifact.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def indicator_active(self, operator: Enum, indicator_active: bool):
        """Filter Active Status based on **indicatorActive** keyword.

        Args:
            operator: The operator enum for the filter.
            indicator_active: A flag indicating whether or not the artifact is active.
        """
        self._tql.add_filter('indicatorActive', operator, indicator_active, TqlType.BOOLEAN)

    def note_id(self, operator: Enum, note_id: int | list):
        """Filter Note ID based on **noteId** keyword.

        Args:
            operator: The operator enum for the filter.
            note_id: The ID of the note associated with this artifact.
        """
        if isinstance(note_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('noteId', operator, note_id, TqlType.INTEGER)

    def source(self, operator: Enum, source: list | str):
        """Filter Source based on **source** keyword.

        Args:
            operator: The operator enum for the filter.
            source: The source of the artifact.
        """
        if isinstance(source, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('source', operator, source, TqlType.STRING)

    def summary(self, operator: Enum, summary: list | str):
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary of the artifact.
        """
        if isinstance(summary, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def task_id(self, operator: Enum, task_id: int | list):
        """Filter Task ID based on **taskId** keyword.

        Args:
            operator: The operator enum for the filter.
            task_id: The ID of the task associated with this artifact.
        """
        if isinstance(task_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('taskId', operator, task_id, TqlType.INTEGER)

    def type(self, operator: Enum, type: list | str):  # pylint: disable=redefined-builtin
        """Filter typeName based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The type name of the artifact.
        """
        if isinstance(type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('type', operator, type, TqlType.STRING)

    def type_name(self, operator: Enum, type_name: list | str):
        """Filter typeName based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The type name of the artifact.
        """
        if isinstance(type_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)
