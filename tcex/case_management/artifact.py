"""ThreatConnect Artifact"""
# standard library
from enum import Enum
from typing import TYPE_CHECKING, Dict, Optional, Union

# first-party
from tcex.case_management.api_endpoints import ApiEndpoints
from tcex.case_management.case import FilterCases
from tcex.case_management.common_case_management import CommonCaseManagement
from tcex.case_management.common_case_management_collection import CommonCaseManagementCollection
from tcex.case_management.filter import Filter
from tcex.case_management.note import FilterNotes
from tcex.case_management.task import FilterTasks
from tcex.case_management.tql import TQL

if TYPE_CHECKING:
    # first-party
    from tcex.case_management.artifact_type import ArtifactType
    from tcex.case_management.case import Case
    from tcex.case_management.note import Note, Notes
    from tcex.case_management.task import Task


class Artifacts(CommonCaseManagementCollection):
    """Artifacts Class for Case Management Collection

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
        initial_response: Initial data in Case Object for Artifact.
        tql_filters: List of TQL filters.
        params: Dict of the params to be sent while retrieving the Artifacts objects.
    """

    def __init__(
        self,
        tcex,
        initial_response: Optional[dict] = None,
        tql_filters: Optional[list] = None,
        params: Optional[dict] = None,
    ) -> None:
        """Initialize Class properties"""
        super().__init__(
            tcex,
            ApiEndpoints.ARTIFACTS,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
        )

        if initial_response:
            for item in initial_response.get('data', []):
                self.added_items.append(Artifact(tcex, **item))

    def __iter__(self) -> 'Artifact':
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def add_artifact(self, artifact: 'Artifact'):
        """Add an Artifact."""
        self.added_items.append(artifact)

    def entity_map(self, entity: dict) -> 'Artifact':
        """Map a dict to a Artifact.

        Args:
            entity (dict): The Artifact data.
        """
        return Artifact(self.tcex, **entity)

    @property
    def filter(self) -> 'FilterArtifacts':
        """Return instance of FilterArtifact Object."""
        return FilterArtifacts(ApiEndpoints.ARTIFACTS, self.tcex, self.tql)


class Artifact(CommonCaseManagement):
    """Artifact object for Case Management.

    Args:
        analytics_priority (str, kwargs): [Read-Only] The **Analytics Priority** for the Artifact.
        analytics_priority_level (int, kwargs): [Read-Only] The **Analytics Priority Level** for
            the Artifact.
        analytics_score (int, kwargs): [Read-Only] The **Analytics Score** for the Artifact.
        analytics_status (int, kwargs): [Read-Only] The **Analytics Status** for the Artifact.
        analytics_type (str, kwargs): [Read-Only] The **Analytics Type** for the Artifact.
        artifact_type (ArtifactType, kwargs): [Read-Only] The **Artifact Type** for the Artifact.
        case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Artifact.
        case_xid (str, kwargs): [Required (alt: caseId)] The **Case Xid** for the Artifact.
        date_added (str, kwargs): [Read-Only] The **Date Added** for the Artifact.
        field_name (str, kwargs): TODO - what is this
        file_data (str, kwargs): Base64 encoded file attachment required only for certain artifact
            types.
        intel_type (str, kwargs): The **Intel Type** for the Artifact.
        links (Link, kwargs): The **Links** for the Artifact.
        notes (Notes, kwargs): a list of Notes corresponding to the Artifact
        parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Artifact.
        source (str, kwargs): The **Source** for the Artifact.
        summary (str, kwargs): [Required] The **Summary** for the Artifact.
        task (Task, kwargs): [Read-Only] The **Task** for the Artifact.
        task_id (int, kwargs): the ID of the task which the Artifact references
        task_xid (str, kwargs): the XID of the task which the Artifact references
        type (str, kwargs): [Required] The **Type** for the Artifact.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.ARTIFACTS, kwargs)
        self.artifact_filter = [
            {
                'keyword': 'artifactId',
                'operator': TQL.Operator.EQ,
                'value': self.id,
                'type': TQL.Type.INTEGER,
            }
        ]

        self._analytics_priority: str = kwargs.get('analytics_priority')
        self._analytics_priority_level: int = kwargs.get('analytics_priority_level')
        self._analytics_score: int = kwargs.get('analytics_score')
        self._analytics_status: int = kwargs.get('analytics_status')
        self._analytics_type: str = kwargs.get('analytics_type')
        self._artifact_type: 'ArtifactType' = kwargs.get('artifact_type')
        self._case_id: int = kwargs.get('case_id') or kwargs.get('parent_case', {}).get('id')
        self._case_xid: str = kwargs.get('case_xid')
        self._date_added: str = kwargs.get('date_added')
        self._field_name: str = kwargs.get('field_name')
        self._file_data: str = kwargs.get('file_data')
        self._intel_type: str = kwargs.get('intel_type')
        self._links = kwargs.get('links')
        self._notes: 'Notes' = kwargs.get('notes')
        self._parent_case: 'Case' = kwargs.get('parent_case')
        self._source: str = kwargs.get('source')
        self._summary: str = kwargs.get('summary')
        self._task: 'Task' = kwargs.get('task')
        self._task_id: int = kwargs.get('task_id')
        self._task_xid: str = kwargs.get('task_xid')
        self._type: str = kwargs.get('type')

    def add_note(self, **kwargs) -> None:
        """Add a Note to a Case."""
        self.notes.add_note(self.tcex.cm.note(**kwargs))

    @property
    def analytics_priority(self) -> str:
        """Return the **Analytics Priority** for the Artifact."""
        return self._analytics_priority

    @property
    def analytics_priority_level(self) -> int:
        """Return the **Analytics Priority Level** for the Artifact."""
        return self._analytics_priority_level

    @property
    def analytics_score(self) -> int:
        """Return the **Analytics Score** for the Artifact."""
        return self._analytics_score

    @property
    def analytics_status(self) -> int:
        """Return the **Analytics Status** for the Artifact."""
        return self._analytics_status

    @property
    def analytics_type(self) -> str:
        """Return the **Analytics Type** for the Artifact."""
        return self._analytics_type

    @property
    def artifact_type(self) -> 'ArtifactType':
        """Return the **Artifact Type** for the Artifact."""
        if self._artifact_type:
            return self.tcex.cm.artifact_type(**self._artifact_type)
        return self._artifact_type

    @property
    def as_entity(self) -> Dict[str, str]:
        """Return the entity representation of the Artifact."""
        return {'type': 'Artifact', 'value': self.summary, 'id': self.id}

    @property
    def case_id(self) -> int:
        """Return the parent **Case ID** for the Artifact."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id: int) -> None:
        """Set the parent **Case ID** for the Artifact."""
        self._case_id = case_id

    @property
    def case_xid(self) -> str:
        """Return the **Case XID** for the Artifact."""
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid: str) -> None:
        """Set the **Case XID** for the Artifact."""
        self._case_xid = case_xid

    @property
    def date_added(self) -> str:
        """Return the **Date Added** for the Artifact."""
        return self._date_added

    def entity_mapper(self, entity: dict) -> None:
        """Update current object with provided object properties.

        Args:
            entity: An entity dict used to update the Object.
        """
        new_artifact = Artifact(self.tcex, **entity)
        self.__dict__.update(new_artifact.__dict__)

    @property
    def field_name(self) -> str:
        """Return the **Field Name** for the Artifact."""
        return self._field_name

    @property
    def file_data(self) -> str:
        """Return the **File Data** for the Artifact."""
        return self._file_data

    @file_data.setter
    def file_data(self, file_data: str) -> None:
        """Set the **File Data** for the Artifact."""
        self._file_data = file_data

    @property
    def intel_type(self) -> str:
        """Return the **Intel Type** for the Artifact."""
        return self._intel_type

    @property
    def links(self) -> str:
        """Return the **Links** for the Artifact."""
        # TODO: create an object for this
        return self._links

    @property
    def notes(self) -> 'Note':
        """Return the **Notes** for the Artifact."""
        if self._notes is None or isinstance(self._notes, dict):
            notes = self._notes or {}
            self._notes = self.tcex.cm.notes(
                initial_response=notes, tql_filters=self.artifact_filter
            )
        return self._notes

    @notes.setter
    def notes(self, notes: Union['Note', dict]) -> None:
        """Set the **Notes** for the Artifact."""
        if isinstance(notes, dict):
            self._notes = self.tcex.cm.notes(
                initial_response=notes, tql_filters=self.artifact_filter
            )
        self._notes = notes

    @property
    def parent_case(self) -> 'Case':
        """Return the **Parent Case** for the Task."""
        if self._parent_case:
            return self.tcex.cm.case(**self._parent_case)
        return self._parent_case

    @property
    def source(self) -> str:
        """Return the **Source** for the Artifact."""
        return self._source

    @source.setter
    def source(self, source: str) -> None:
        """Set the **Source** for the Artifact."""
        self._source = source

    @property
    def summary(self) -> str:
        """Return the **Summary** for the Artifact."""
        return self._summary

    @summary.setter
    def summary(self, summary: str) -> None:
        """Set the **Summary** for the Artifact."""
        self._summary = summary

    @property
    def task(self) -> 'Task':
        """Return the **Task** for the Artifact."""
        if self._task:
            return self.tcex.cm.task(**self._task)
        return self._task

    @property
    def task_id(self) -> int:
        """Return the **Task ID** for the Artifact."""
        return self._task_id

    @task_id.setter
    def task_id(self, task_id: int) -> None:
        """Set the **Task ID** for the Artifact."""
        self._task_id = task_id

    @property
    def task_xid(self) -> str:
        """Return the **Task XID** for the Artifact."""
        return self._task_xid

    @task_xid.setter
    def task_xid(self, task_xid: str) -> None:
        """Set the **Task XID** for the Artifact."""
        self._task_xid = task_xid

    @property
    def type(self) -> str:
        """Return the **Type** for the Artifact."""
        return self._type

    @type.setter
    def type(self, artifact_type: str) -> None:
        """Set the **Type** for the Artifact."""
        self._type = artifact_type


class FilterArtifacts(Filter):
    """Filter Object for Artifacts"""

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Artifacts based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case associated with this artifact.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    @property
    def has_case(self) -> 'FilterCases':
        """Return **FilterCases** for further filtering."""
        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    @property
    def has_note(self) -> 'FilterNotes':
        """Return **FilterNotes** for further filtering."""
        notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    @property
    def has_task(self) -> 'FilterTasks':
        """Return **FilterTask** for further filtering."""
        tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator: Enum, id_: int):
        """Filter Artifacts based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id_: The ID of the artifact.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

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

    def type_name(self, operator: Enum, type_name: str):
        """Filter Artifacts based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The type name of the artifact.
        """
        self._tql.add_filter('typeName', operator, type_name, TQL.Type.STRING)
