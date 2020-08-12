# -*- coding: utf-8 -*-
"""ThreatConnect Artifact"""

from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


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
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Artifacts objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
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

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def add_artifact(self, artifact):
        """Add an Artifact.

        Args:
            artifact (Artifact): The Artifact Object to add.
        """
        self.added_items.append(artifact)

    def entity_map(self, entity):
        """Map a dict to a Artifact.

        Args:
            entity (dict): The Artifact data.

        Returns:
            CaseManagement.Artifact: An Artifact Object
        """
        return Artifact(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterArtifact Object."""
        return FilterArtifacts(ApiEndpoints.ARTIFACTS, self.tcex, self.tql)


class Artifact(CommonCaseManagement):
    """Artifact object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
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
        file_data (str, kwargs): Base64 encoded file attachment required only for certain artifact
            types
        intel_type (str, kwargs): The **Intel Type** for the Artifact.
        links (Link, kwargs): The **Links** for the Artifact.
        notes (Note, kwargs): a list of Notes corresponding to the Artifact
        parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Artifact.
        source (str, kwargs): The **Source** for the Artifact.
        summary (str, kwargs): [Required] The **Summary** for the Artifact.
        task (case_management.task.Task, kwargs): [Read-Only] The **Task** for the Artifact.
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

        self._analytics_priority = kwargs.get('analytics_priority', None)
        self._analytics_priority_level = kwargs.get('analytics_priority_level', None)
        self._analytics_score = kwargs.get('analytics_score', None)
        self._analytics_status = kwargs.get('analytics_status', None)
        self._analytics_type = kwargs.get('analytics_type', None)
        self._artifact_type = kwargs.get('artifact_type', None)
        self._case_id = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get('id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._date_added = kwargs.get('date_added', None)
        self._field_name = kwargs.get('field_name', None)
        self._file_data = kwargs.get('file_data', None)
        self._intel_type = kwargs.get('intel_type', None)
        self._links = kwargs.get('links', None)
        self._notes = kwargs.get('notes', None)
        self._parent_case = kwargs.get('parent_case', None)
        self._source = kwargs.get('source', None)
        self._summary = kwargs.get('summary', None)
        self._task = kwargs.get('task', None)
        self._task_id = kwargs.get('task_id', None)
        self._task_xid = kwargs.get('task_xid', None)
        self._type = kwargs.get('type', None)

    def add_note(self, **kwargs):
        """Add a Note to a Case."""
        self.notes.add_note(self.tcex.cm.note(**kwargs))

    @property
    def analytics_priority(self):
        """Return the **Analytics Priority** for the Artifact."""
        return self._analytics_priority

    @property
    def analytics_priority_level(self):
        """Return the **Analytics Priority Level** for the Artifact."""
        return self._analytics_priority_level

    @property
    def analytics_score(self):
        """Return the **Analytics Score** for the Artifact."""
        return self._analytics_score

    @property
    def analytics_status(self):
        """Return the **Analytics Status** for the Artifact."""
        return self._analytics_status

    @property
    def analytics_type(self):
        """Return the **Analytics Type** for the Artifact."""
        return self._analytics_type

    @property
    def artifact_type(self):
        """Return the **Artifact Type** for the Artifact."""
        if self._artifact_type:
            return self.tcex.cm.artifact_type(**self._artifact_type)
        return self._artifact_type

    @property
    def as_entity(self):
        """Return the entity representation of the Artifact."""
        return {'type': 'Artifact', 'value': self.summary, 'id': self.id}

    @property
    def case_id(self):
        """Return the parent **Case ID** for the Artifact."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the parent **Case ID** for the Artifact."""
        self._case_id = case_id

    @property
    def case_xid(self):
        """Return the **Case XID** for the Artifact."""
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        """Set the **Case XID** for the Artifact."""
        self._case_xid = case_xid

    @property
    def date_added(self):
        """Return the **Date Added** for the Artifact."""
        return self._date_added

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_artifact = Artifact(self.tcex, **entity)
        self.__dict__.update(new_artifact.__dict__)

    @property
    def field_name(self):
        """Return the **File Data** for the Artifact."""
        return self._field_name

    @property
    def file_data(self):
        """Return the **File Data** for the Artifact."""
        return self._file_data

    @file_data.setter
    def file_data(self, file_data):
        """Set the **File Data** for the Artifact."""
        self._file_data = file_data

    @property
    def intel_type(self):
        """Return the **Intel Type** for the Artifact."""
        return self._intel_type

    @property
    def links(self):
        """Return the **Links** for the Artifact."""
        # TODO: create an object for this
        return self._links

    @property
    def notes(self):
        """Return the **Notes** for the Artifact."""
        if self._notes is None or isinstance(self._notes, dict):
            notes = self._notes or {}
            self._notes = self.tcex.cm.notes(
                initial_response=notes, tql_filters=self.artifact_filter
            )
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the **Notes** for the Artifact."""
        if isinstance(notes, dict):
            self._notes = self.tcex.cm.notes(
                initial_response=notes, tql_filters=self.artifact_filter
            )
        self._notes = notes

    @property
    def parent_case(self):
        """Return the **Parent Case** for the Task."""
        if self._parent_case:
            return self.tcex.cm.case(**self._parent_case)
        return self._parent_case

    @property
    def source(self):
        """Return the **Source** for the Artifact."""
        return self._source

    @source.setter
    def source(self, source):
        """Set the **Source** for the Artifact."""
        self._source = source

    @property
    def summary(self):
        """Return the **Summary** for the Artifact."""
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Set the **Summary** for the Artifact."""
        self._summary = summary

    @property
    def task(self):
        """Return the **Task** for the Note."""
        if self._task:
            return self.tcex.cm.task(**self._task)
        return self._task

    @property
    def task_id(self):
        """Return the **Task ID** for the Artifact."""
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """Set the **Task ID** for the Artifact."""
        self._task_id = task_id

    @property
    def task_xid(self):
        """Return the **Task XID** for the Artifact."""
        return self._task_xid

    @task_xid.setter
    def task_xid(self, task_xid):
        """Set the **Task XID** for the Artifact."""
        self._task_xid = task_xid

    @property
    def type(self):
        """Return the **Type** for the Artifact."""
        return self._type

    @type.setter
    def type(self, artifact_type):
        """Set the **Type** for the Artifact."""
        self._type = artifact_type


class FilterArtifacts(Filter):
    """Filter Object for Artifacts"""

    def case_id(self, operator, case_id):
        """Filter Artifacts based on **caseId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case associated with this artifact.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from .case import FilterCases

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        from .note import FilterNotes  # pylint: disable=cyclic-import

        notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

    @property
    def has_task(self):
        """Return **FilterTask** for further filtering."""
        from .task import FilterTasks  # pylint: disable=cyclic-import

        tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Artifacts based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the artifact.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def note_id(self, operator, note_id):
        """Filter Artifacts based on **noteId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            note_id (int): The ID of the note associated with this artifact.
        """
        self._tql.add_filter('noteId', operator, note_id, TQL.Type.INTEGER)

    def source(self, operator, source):
        """Filter Artifacts based on **source** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            source (str): The source of the artifact.
        """
        self._tql.add_filter('source', operator, source, TQL.Type.STRING)

    def summary(self, operator, summary):
        """Filter Artifacts based on **summary** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            summary (str): The summary of the artifact.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def task_id(self, operator, task_id):
        """Filter Artifacts based on **taskId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            task_id (int): The ID of the task associated with this artifact.
        """
        self._tql.add_filter('taskId', operator, task_id, TQL.Type.INTEGER)

    def type_name(self, operator, type_name):
        """Filter Artifacts based on **typeName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            type_name (str): The type name of the artifact.
        """
        self._tql.add_filter('typeName', operator, type_name, TQL.Type.STRING)
