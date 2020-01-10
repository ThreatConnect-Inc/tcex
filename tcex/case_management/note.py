# -*- coding: utf-8 -*-
"""ThreatConnect Note"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL


class Notes(CommonCaseManagementCollection):
    """ThreatConnect Notes Object

    params example: {
        'result_limit': 100, # How many results are retrieved.
        'result_start': 10,  # Starting point on retrieved results.
        'fields': ['caseId', 'summary'] # Additional fields returned on the results
    }

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
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

    def __str__(self):
        """Object iterator"""
        printable_string = ''
        for obj in self.iterate(initial_response=self.initial_response):
            printable_string += f'{"-" * 50}\n'
            printable_string += str(obj)
        return printable_string

    def add_note(self, note):
        """Add a Note to an Artifact, Case, or Task.

        Args:
            note (Note): The Note Object to add.
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
        """Return instance of FilterNote Object."""
        return FilterNote(self.tql)


class Note(CommonCaseManagement):
    """Note object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        # possibly parent_artifact
        artifact (dict, kwargs): The Artifact for the Note.
        artifact_id (int, kwargs): The Artifact ID for the Note.
        case_id (int, kwargs): The Case ID for the Note.
        case_xid (str, kwargs): The Task xid for the Note.
        date_added (date, kwargs): The Date Added for the Note.
        edited (bool, kwargs): The Edited for the Note.
        last_modified (date, kwargs): The Last Modified for the Note.
        parent_case (dict, kwargs): The Parent Case for the Artifact.
        summary (str, kwargs): The Summary for the Note.
        # possibly parent_artifact
        task (dict, kwargs): The Task for the Note.
        task_id (int, kwargs): The Task ID for the Note.
        task_xid (str, kwargs): The Task xid for the Note.
        text (str, kwargs): The Text for the Note.
        user_id (int, kwargs): The User ID for the Note.
        user_name (str, kwargs): The User Name for the Note.
        workflow_event (dict, kwargs): The Workflow Event for the Note.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize class properties."""
        super().__init__(tcex, ApiEndpoints.NOTES, kwargs)
        # TODO: @bpurdy - should we handle this as on object and dict?
        self._artifact = tcex.cm.artifact(**kwargs.get('artifact', {}))
        self._artifact_id = kwargs.get('artifact_id', None)
        self._case_id = kwargs.get('case_id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._date_added = kwargs.get('date_added')
        self._edited = kwargs.get('edited', None)
        self._last_modified = kwargs.get('last_modified', None)
        self._parent_case = tcex.cm.case(**kwargs.get('parent_case', {}))
        self._summary = kwargs.get('summary', None)
        self._task = tcex.cm.task(**kwargs.get('task', {}))
        self._task_id = kwargs.get('task_id', None)
        self._task_xid = kwargs.get('task_xid', None)
        self._text = kwargs.get('text', None)
        self._user_id = kwargs.get('user_id', None)
        self._user_name = kwargs.get('user_name', None)
        self._workflow_event = tcex.cm.workflow_event(**kwargs.get('workflow_event', {}))
        self._workflow_event_id = kwargs.get('workflow_event_id', None)

    @property
    def artifact(self):
        """Return the parent **Artifact** for the Note."""
        return self._artifact

    @property
    def artifact_id(self):
        """Return the parent "Artifact ID" for the Note."""
        return self._artifact_id

    @artifact_id.setter
    def artifact_id(self, artifact_id):
        """Set the parent "Artifact ID" for the Note."""
        self._artifact_id = artifact_id

    @property
    def as_entity(self):
        """Return the entity representation of the Note."""
        return {'type': 'Note', 'value': self.summary, 'id': self.id}

    @property
    def available_fields(self):
        """Return the available fields to fetch for a Note."""
        return ['artifacts', 'caseId', 'task', 'parentCase']

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_note = Note(self.tcex, **entity)
        self.__dict__.update(new_note.__dict__)

    @property
    def case_id(self):
        """Return the parent "Case ID" for the Note."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the parent "Case ID" for the Note."""
        self._case_id = case_id

    @property
    def case_xid(self):
        """Return the parent "Case XID" for the Note."""
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        """Set the parent "Case XID" for the Note."""
        self._case_xid = case_xid

    @property
    def date_added(self):
        """Return the "Date Added" value for the Note."""
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """Set the "Date Added" value for the Note."""
        self._date_added = date_added

    @property
    def edited(self):
        """Return the "Edited" value for the Note."""
        return self._edited

    @edited.setter
    def edited(self, edited):
        """Set the "Edited" value for the Note."""
        self._edited = edited

    @property
    def last_modified(self):
        """Return the "Last Modified" value for the Note."""
        return self._last_modified

    @last_modified.setter
    def last_modified(self, last_modified):
        """Set the "Last Modified" value for the Note."""
        self._last_modified = last_modified

    @property
    def parent_case(self):
        """Return the **Parent Case** for the Artifact."""
        return self._parent_case

    @property
    def required_properties(self):
        """Return a list of required fields for an Artifact."""
        return ['text']

    @property
    def summary(self):
        """Return the "Summary" value for the Note."""
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Set the "Summary" value for the Note."""
        self._summary = summary

    @property
    def task(self):
        """Return the **Task** for the Artifact."""
        return self._task

    @property
    def task_id(self):
        """Return the parent "Task ID" for the Note."""
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """Set the parent "Task ID" for the Note."""
        self._task_id = task_id

    @property
    def task_xid(self):
        """Return the parent "Task XID" for the Note."""
        return self._task_xid

    @task_xid.setter
    def task_xid(self, task_xid):
        """Set the parent "Task XID" for the Note."""
        self._task_xid = task_xid

    @property
    def text(self):
        """Return the "Text" value for the Note."""
        return self._text

    @text.setter
    def text(self, text):
        """Set the "Text" value for the Note."""
        self._text = text

    @property
    def user_id(self):
        """Return the parent "User ID" for the Note."""
        return self._user_id

    @property
    def user_name(self):
        """Return the "User Name" value for the Note."""
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """Set the "User Name" value for the Note."""
        self._user_name = user_name

    @property
    def workflow_event(self):
        """Return the **Workflow Event** for the Artifact."""
        return self._workflow_event

    @property
    def workflow_event_id(self):
        """Return the "Workflow Event ID" value for the Note."""
        return self._workflow_event_id

    @workflow_event_id.setter
    def workflow_event_id(self, workflow_event_id):
        """Set the "Workflow Event ID" value for the Note."""
        self._workflow_event_id = workflow_event_id


class FilterNote:
    """Filter Object for Note

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self._tql = tql

    def artifact_id(self, operator, artifact_id):
        """Filter objects based on "artifact id" field.

        Args:
            operator (enum): The enum for the required operator.
            artifact_id (int): The filter value.
        """
        self._tql.add_filter('artifactid', operator, artifact_id, TQL.Type.INTEGER)

    def author(self, operator, author):
        """Filter objects based on "author" field.

        For API HMAC auth the author is the Access ID, otherwise the Account login username.

        Args:
            operator (enum): The enum for the required operator.
            author (str): The filter value.
        """
        self._tql.add_filter('author', operator, author)

    def case_id(self, operator, case_id):
        """Filter objects based on "case id" field.

        Args:
            operator (enum): The enum for the required operator.
            case_id (str): The filter value.
        """
        self._tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator, date_added):
        """Filter objects based on "date added" field.

        Args:
            operator (enum): The enum for the required operator.
            date_added (str): The filter value.
        """
        self._tql.add_filter('dateadded', operator, date_added)

    def id(self, operator, id_):
        """Filter objects based on "id" field.

        Args:
            operator (enum): The enum for the required operator.
            id (int): The filter value.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    @property
    def keywords(self):
        """Return supported TQL keywords."""
        keywords = []
        for prop in dir(self):
            if prop.startswith('_') or prop in ['tql']:
                continue
            # remove underscore from method name to match keyword
            keywords.append(prop.replace('_', ''))

        return keywords

    def last_modified(self, operator, last_modified):
        """Filter objects based on "last modified" field.

        Args:
            operator (enum): The enum for the required operator.
            last_modified (int): The filter value.
        """
        self._tql.add_filter('lastmodified', operator, last_modified)

    def summary(self, operator, summary):
        """Filter objects based on "summary" field.

        Args:
            operator (enum): The enum for the required operator.
            summary (int): The filter value.
        """
        self._tql.add_filter('summary', operator, summary)

    def task_id(self, operator, task_id):
        """Filter objects based on "task id" field.

        Args:
            operator (enum): The enum for the required operator.
            task_id (int): The filter value.
        """
        self._tql.add_filter('taskid', operator, task_id, TQL.Type.INTEGER)

    def tql(self, tql):
        """Filter objects based on TQL expression.

        Args:
            tql (str): The raw TQL string for the filter.
        """
        self._tql.set_raw_tql(tql)

    def workflow_event_id(self, operator, workflow_event_id):
        """Filter objects based on "workflow event id" field.

        Args:
            operator (enum): The enum for the required operator.
            task_id (int): The filter value.
        """
        self._tql.add_filter('workfloweventid', operator, workflow_event_id, TQL.Type.INTEGER)
