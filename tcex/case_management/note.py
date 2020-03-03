# -*- coding: utf-8 -*-
"""ThreatConnect Note"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class Notes(CommonCaseManagementCollection):
    """ThreatConnect Notes Object

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
            Case Object for Note. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Notes objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.NOTES,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
        )
        if initial_response:
            for item in initial_response.get('data', []):
                self.added_items.append(Note(tcex, **item))

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def add_note(self, note):
        """Add a Note.

        Args:
            note (case_management.note.Note): The Note Object to add.
        """
        self.added_items.append(note)

    def entity_map(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): The dict to map self too.
        """
        return Note(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterNotes Object."""
        return FilterNotes(ApiEndpoints.NOTES, self.tcex, self.tql)


class Note(CommonCaseManagement):
    """Note object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        artifact (Artifact, kwargs): [Read-Only] The **Artifact** for the Note.
        artifact_id (int, kwargs): the ID of the Artifact on which to apply the Note
        author (int, kwargs): [Read-Only] The **Author** for the Note.
        case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Note.
        case_xid (str, kwargs): [Required (alt: caseId)]
        date_added (str, kwargs): [Read-Only] The **Date Added** for the Note.
        edited (boolean, kwargs): [Read-Only] The **Edited** for the Note.
        last_modified (str, kwargs): [Read-Only] The **Last Modified** for the Note.
        parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Note.
        summary (str, kwargs): [Read-Only] The **Summary** for the Note.
        task (case_management.task.Task, kwargs): [Read-Only] The **Task** for the Note.
        task_id (int, kwargs): the ID of the Task on which to apply the Note
        task_xid (str, kwargs): the XID of the Task on which to apply the Note
        text (str, kwargs): [Required] The **Text** for the Note.
        workflow_event (WorkflowEvent, kwargs): [Read-Only] The **Workflow Event** for the Note.
        workflow_event_id (int, kwargs): the ID of the Event on which to apply the Note
    """

    def __init__(self, tcex, **kwargs):
        """Initialize class properties."""
        super().__init__(tcex, ApiEndpoints.NOTES, kwargs)

        self._artifact = kwargs.get('artifact', None)
        self._artifact_id = kwargs.get('artifact_id', None)
        self._author = kwargs.get('author', None)
        self._case_id = kwargs.get('case_id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._date_added = kwargs.get('date_added')
        self._edited = kwargs.get('edited', None)
        self._last_modified = kwargs.get('last_modified', None)
        self._parent_case = kwargs.get('parent_case', None)
        self._summary = kwargs.get('summary', None)
        self._task = kwargs.get('task', None)
        self._task_id = kwargs.get('task_id', None)
        self._task_xid = kwargs.get('task_xid', None)
        self._text = kwargs.get('text', None)
        self._workflow_event = kwargs.get('workflow_event', None)
        self._workflow_event_id = kwargs.get('workflow_event_id', None)

    @property
    def artifact(self):
        """Return the parent **Artifact** for the Note."""
        if self._artifact:
            return self.tcex.cm.artifact(**self._artifact)
        return self._artifact

    @property
    def artifact_id(self):
        """Return the parent **Artifact ID** for the Note."""
        return self._artifact_id

    @artifact_id.setter
    def artifact_id(self, artifact_id):
        """Set the parent **Artifact ID** for the Note."""
        self._artifact_id = artifact_id

    @property
    def as_entity(self):
        """Return the entity representation of the Note."""
        return {'type': 'Note', 'value': self.summary, 'id': self.id}

    @property
    def author(self):
        """Return the parent **Author** for the Note."""
        return self._author

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_note = Note(self.tcex, **entity)
        self.__dict__.update(new_note.__dict__)

    @property
    def case_id(self):
        """Return the parent **Case ID** for the Note."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the parent **Case ID** for the Note."""
        self._case_id = case_id

    @property
    def case_xid(self):
        """Return the parent **Case XID** for the Note."""
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        """Set the parent **Case XID** for the Note."""
        self._case_xid = case_xid

    @property
    def date_added(self):
        """Return the **Date Added** value for the Note."""
        return self._date_added

    @property
    def edited(self):
        """Return the **Edited** value for the Note."""
        return self._edited

    @property
    def last_modified(self):
        """Return the **Last Modified** value for the Note."""
        return self._last_modified

    @property
    def parent_case(self):
        """Return the **Parent Case** for the Task."""
        if self._parent_case:
            return self.tcex.cm.case(**self._parent_case)
        return self._parent_case

    @property
    def summary(self):
        """Return the **Summary** value for the Note."""
        return self._summary

    @property
    def task(self):
        """Return the **Task** for the Note."""
        if self._task:
            return self.tcex.cm.task(**self._task)
        return self._task

    @property
    def task_id(self):
        """Return the **Task ID** for the Note."""
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """Set the **Task ID** for the Note."""
        self._task_id = task_id

    @property
    def task_xid(self):
        """Return the **Task XID** for the Note."""
        return self._task_xid

    @task_xid.setter
    def task_xid(self, task_xid):
        """Set the **Task XID** for the Note."""
        self._task_xid = task_xid

    @property
    def text(self):
        """Return the **Text** value for the Note."""
        return self._text

    @text.setter
    def text(self, text):
        """Set the **Text** value for the Note."""
        self._text = text

    @property
    def workflow_event(self):
        """Return the **Workflow Event** for the Note."""
        if self._workflow_event:
            return self.tcex.cm.workflow_event(**self._workflow_event)
        return self._workflow_event

    @property
    def workflow_event_id(self):
        """Return the **Workflow Event ID** value for the Note."""
        return self._workflow_event_id

    @workflow_event_id.setter
    def workflow_event_id(self, workflow_event_id):
        """Set the **Workflow Event ID** value for the Note."""
        self._workflow_event_id = workflow_event_id


class FilterNotes(Filter):
    """Filter Object for Notes"""

    def artifact_id(self, operator, artifact_id):
        """Filter Notes based on **artifactId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            artifact_id (int): The ID of the artifact this note is associated with.
        """
        self._tql.add_filter('artifactId', operator, artifact_id, TQL.Type.INTEGER)

    def author(self, operator, author):
        """Filter Notes based on **author** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            author (str): The account login of the user who wrote the note.
        """
        self._tql.add_filter('author', operator, author, TQL.Type.STRING)

    def case_id(self, operator, case_id):
        """Filter Notes based on **caseId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case this note is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator, date_added):
        """Filter Notes based on **dateAdded** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            date_added (str): The date the note was written.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    @property
    def has_artifact(self):
        """Return **FilterArtifacts** for further filtering."""
        from .artifact import FilterArtifacts

        artifacts = FilterArtifacts(ApiEndpoints.ARTIFACTS, self._tcex, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from .case import FilterCases

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    @property
    def has_task(self):
        """Return **FilterTask** for further filtering."""
        from .task import FilterTasks  # pylint: disable=cyclic-import

        tasks = FilterTasks(ApiEndpoints.TASKS, self._tcex, TQL())
        self._tql.add_filter('hasTask', TQL.Operator.EQ, tasks, TQL.Type.SUB_QUERY)
        return tasks

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Notes based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the case.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def last_modified(self, operator, last_modified):
        """Filter Notes based on **lastModified** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            last_modified (str): The date the note was last modified.
        """
        self._tql.add_filter('lastModified', operator, last_modified, TQL.Type.STRING)

    def summary(self, operator, summary):
        """Filter Notes based on **summary** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            summary (str): Text of the first 100 characters of the note.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def task_id(self, operator, task_id):
        """Filter Notes based on **taskId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            task_id (int): The ID of the task this note is associated with.
        """
        self._tql.add_filter('taskId', operator, task_id, TQL.Type.INTEGER)

    def workflow_event_id(self, operator, workflow_event_id):
        """Filter Notes based on **workflowEventId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            workflow_event_id (int): The ID of the workflow event this note is associated with.
        """
        self._tql.add_filter('workflowEventId', operator, workflow_event_id, TQL.Type.INTEGER)
