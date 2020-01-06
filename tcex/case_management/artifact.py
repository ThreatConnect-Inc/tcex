# -*- coding: utf-8 -*-
"""ThreatConnect Artifact"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .note import Note, Notes
from .tql import TQL


class Artifacts(CommonCaseManagementCollection):
    """Artifacts Class for Case Management Collection

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties"""
        super().__init__(
            tcex,
            ApiEndpoints.ARTIFACTS,
            initial_response=initial_response,
            tql_filters=tql_filters,
        )
        self.added_artifacts = []

        if initial_response:
            for t in initial_response.get('data', []):
                self.added_artifacts.append(t)

    def __iter__(self):
        """Object iterator"""
        return self.iterate(
            initial_response=self.initial_response, added_entities=self.added_artifacts
        )

    def add_artifact(self, artifact):
        """Add an artifact to a case.

        Args:
            artifact (Artifact): The Artifact Object to add.
        """
        self.added_artifacts.append(artifact)

    @property
    def as_dict(self):
        """Returns a dict version of this object."""
        # @bpurdy - does this include all artifacts ???
        return super().list_as_dict(self.added_artifacts)

    def entity_map(self, entity):
        """Map a dict to a Artifact.

        Args:
            entity (dict): The Artifact data.

        Returns:
            CaseManagement.Artifact: [description]
        """
        return Artifact(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterArtifact Object."""
        return FilterArtifact(self.tql)


class Artifact(CommonCaseManagement):
    """Artifact object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        case_id (int, kwargs): The Case ID for the artifact.
        case_xid (str, kwargs): The Case XID for the artifact
        date_added (date, kwargs): The date added for the artifact
        file_data (base64, kwargs): The file data for the artifact
        intel_type (str, kwargs): The intel type for the artifact.
        notes (dict, kwargs): The notes for the artifact.
        source (str, kwargs): The source for the artifact.
        summary (str, kwargs): The summary for the artifact.
        task_id (int, kwargs): The Task ID for the artifact.
        task_xid (str, kwargs): The task xid for the artifact.
        type (str, kwargs): The Artifact Type for the artifact.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.ARTIFACTS, kwargs)

        self._case_id = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get('id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._date_added = kwargs.get('date_added', None)
        self._file_data = kwargs.get('file_data', None)
        self._intel_type = kwargs.get('intel_type', None)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}).get('data'))
        self._source = kwargs.get('source', None)
        self._summary = kwargs.get('summary', None)
        self._task_id = kwargs.get('task_id', None)
        self._task_xid = kwargs.get('task_xid', None)
        self._type = kwargs.get('type', None)

    def add_note(self, **kwargs):
        """Add a note to the artifact"""
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def as_entity(self):
        """
        Return the entity representation of the Artifact
        """
        return {'type': 'Artifact', 'value': self.summary, 'id': self.id}

    @property
    def available_fields(self):
        """Return the available fields to fetch for an Artifact.

        Returns:
            list: Available fields to fetch for the artifact.
        """
        return [
            'caseXid',
            'caseId',
            'fileData',
            'intelType',
            'notes',
            'source',
            'summary',
            'taskId',
            'taskXid',
            'type',
        ]

    @property
    def case_id(self):
        """Return the parent Case ID for the Artifact."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the parent Case ID for the Artifact."""
        self._case_id = case_id

    @property
    def case_xid(self):
        """Return the Case XID for the Artifact."""
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        """Set the Case XID for the Artifact."""
        self._case_xid = case_xid

    @property
    def date_added(self):
        """Return the Date Added for the Artifact."""
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """Set the Date Added for the Artifact."""
        self._date_added = date_added

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): The dict to map self too.
        """
        new_artifact = Artifact(self.tcex, **entity)
        self.__dict__.update(new_artifact.__dict__)

    @property
    def file_data(self):
        """Return the File Data for the Artifact."""
        return self._file_data

    @file_data.setter
    def file_data(self, file_data):
        """Set the File Data for the Artifact."""
        self._file_data = file_data

    @property
    def intel_type(self):
        """Return the Intel Type for the Artifact."""
        return self._intel_type

    @intel_type.setter
    def intel_type(self, intel_type):
        """Set the Intel Type for the Artifact."""
        self._intel_type = intel_type

    @property
    def notes(self):
        """Return the Notes for the Artifact."""
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the Notes for the Artifact."""
        self._notes = notes

    @property
    def required_properties(self):
        """Return a list of required fields for an Artifact.

        Returns:
            list: Required fields for a artifact.
        """
        return ['summary', 'type', 'intel_type', 'case_id']

    @property
    def source(self):
        """Return the Source for the Artifact."""
        return self._source

    @source.setter
    def source(self, source):
        """Set the Source for the Artifact."""
        self._source = source

    @property
    def summary(self):
        """Return the Summary for the Artifact."""
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Set the Summary for the Artifact."""
        self._summary = summary

    @property
    def task_id(self):
        """Return the Task ID for the Artifact."""
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """Set the Task ID for the Artifact."""
        self._task_id = task_id

    @property
    def task_xid(self):
        """Return the Task XID for the Artifact."""
        return self._task_id

    @task_xid.setter
    def task_xid(self, task_xid):
        """Set the Task XID for the Artifact."""
        self._task_id = task_xid

    @property
    def type(self):
        """Return the Type for the Artifact."""
        return self._type

    @type.setter
    def type(self, artifact_type):
        """Set the Type for the Artifact."""
        self._type = artifact_type


class FilterArtifact:
    """Filter Object for Artifact

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self.tql = tql

    def summary(self, operator, summary):
        """Filter objects based on summary field.

        Args:
            operator (enum): The enum for the required operator.
            summary (str): The filter value.
        """
        self.tql.add_filter('summary', operator, summary)

    def case_id(self, operator, case_id):
        """Filter objects based on case id field.

        Args:
            operator (enum): The enum for the required operator.
            case_id (int): The filter value.
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def comment_id(self, operator, comment_id):
        """Filter objects based on comment id field.

        Args:
            operator (enum): The enum for the required operator.
            comment_id (int): The filter value.
        """
        self.tql.add_filter('comment_id', operator, comment_id, TQL.Type.INTEGER)

    def id(self, operator, artifact_id):
        """Filter objects based on ID field.

        Args:
            operator (enum): The enum for the required operator.
            artifact_id (int): The filter value.
        """
        self.tql.add_filter('id', operator, artifact_id, TQL.Type.INTEGER)

    def source(self, operator, source):
        """Filter objects based on source field.

        Args:
            operator (enum): The enum for the required operator.
            source (str): The filter value.
        """
        self.tql.add_filter('source', operator, source)

    def case(self, operator, case):
        """Filter objects based on case association.

        Args:
            operator (enum): The enum for the required operator.
            case (str): The filter value.
        """
        self.tql.add_filter('case', operator, case)

    def task_id(self, operator, task_id):
        """Filter objects based on task id field.

        Args:
            operator (enum): The enum for the required operator.
            task_id (str): The filter value.
        """
        self.tql.add_filter('taskid', operator, task_id, TQL.Type.INTEGER)

    def type_name(self, operator, type_name):
        """Filter objects based on type name field.

        Args:
            operator (enum): The enum for the required operator.
            type_name (str): The filter value.
        """
        self.tql.add_filter('typename', operator, type_name)
