# -*- coding: utf-8 -*-
"""ThreatConnect Artifact"""
from .note import Note, Notes
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL

api_endpoint = '/v3/artifacts'


class Artifacts(CommonCaseManagementCollection):
    """ A iterable class to fetch Artifacts """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """
        Initialization of the class

        Args:
            tcex:
            initial_response: Initial entity to map to.
            tql_filters: TQL filters to apply during a search.
        """
        super().__init__(
            tcex, api_endpoint, initial_response=initial_response, tql_filters=tql_filters
        )
        self.added_artifacts = []

        if initial_response:
            for t in initial_response.get('data', []):
                self.added_artifacts.append(t)

    def summary_filter(self, operator, summary):
        """
            The summary of the artifact
        """
        self.tql.add_filter('summary', operator, summary)

    def case_id_filter(self, operator, case_id):
        """
            The ID of the case associated with this artifact
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def comment_id_filter(self, operator, comment_id):
        """
            The ID of the comment associated with this artifact
        """
        self.tql.add_filter('commentid', operator, comment_id, TQL.Type.INTEGER)

    def id_filter(self, operator, artifact_id):
        """
            The ID of the artifact
        """
        self.tql.add_filter('id', operator, artifact_id, TQL.Type.INTEGER)

    def source_filter(self, operator, source):
        """
            The source of the artifact
        """
        self.tql.add_filter('source', operator, source)

    def case_filter(self, operator, case):
        """
            A nested query for association to other cases
        """
        self.tql.add_filter('case', operator, case)

    def task_id_filter(self, operator, task_id):
        """
            The ID of the task associated with this artifact
        """
        self.tql.add_filter('taskid', operator, task_id, TQL.Type.INTEGER)

    def type_name_filter(self, operator, type_name):
        """
            The type name of the artifact
        """
        self.tql.add_filter('typename', operator, type_name)

    def __iter__(self):
        """
        Iterates over the artifacts using the provided or applied tql filters.
        """
        return self.iterate(
            initial_response=self.initial_response, added_entities=self.added_artifacts
        )

    def entity_map(self, entity):
        """
        Maps a dict to a Artifact.
        """
        return Artifact(self.tcex, **entity)

    def add_artifact(self, artifact):
        """
        Adds the provided artifact to a list of artifacts to be added.
        """
        self.added_artifacts.append(artifact)

    @property
    def as_dict(self):
        """
        Returns a dict version of this object.
        """
        return super().list_as_dict(self.added_artifacts)


class Artifact(CommonCaseManagement):
    """Unique API calls for Artifact API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """
        Initializes the Artifacts class:
        Args:
            tcex:
            case_id (int): The Case ID for the artifact.
            case_xid (str): The Case XID for the artifact
            date_added (date): The date added for the artifact
            file_data (base64): The file data for the artifact
            intel_type (str): The intel type for the artifact.
            notes (dict): The notes for the artifact.
            source (str): The source for the artifact.
            summary (str): The summary for the artifact.
            task_id (int): The Task ID for the artifact.
            task_xid (str): The task xid for the artifact.
            type (str): The Artifact Type for the artifact.
        """
        super().__init__(tcex, api_endpoint, kwargs)
        self._case_id = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get('id', None)
        self._date_added = kwargs.get('date_added', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._file_data = kwargs.get('file_data', None)
        self._intel_type = kwargs.get('intel_type', None)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}).get('data'))
        self._source = kwargs.get('source', None)
        self._summary = kwargs.get('summary', None)
        self._task_id = kwargs.get('task_id', None)
        self._task_xid = kwargs.get('task_xid', None)
        self._type = kwargs.get('type', None)
        self._xid = None

    def add_note(self, **kwargs):
        """
        Adds a note to the artifact
        """
        self._notes.add_note(Note(self.tcex, **kwargs))

    def entity_mapper(self, entity):
        """
        Maps a dict to a Artifact then updates self.

        Args:
            entity (dict): The dict to map self too.
        """
        new_case = Artifact(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def required_properties(self):
        """
        The required fields for a Artifact
        Returns:
            list of required fields for a artifact.
        """
        return ['summary', 'type', 'intel_type', 'case_id']

    @property
    def available_fields(self):
        """
        The available fields to fetch for the artifact.
        Returns:
            list of available fields to fetch for the artifact.
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
    def xid(self):
        """
        xid for the Artifact
        Returns:
            xid for the Artifact
        """
        return self._xid

    @xid.setter
    def xid(self, xid):
        """
        Sets the xid of the Artifact
        Args:
            xid (str): The xid to set for the Artifact

        """
        self._xid = xid

    @property
    def case_id(self):
        """
         The current Case id for the artifact.
         """
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """
        Sets the case id for the Artifact
        """
        self._case_id = case_id

    @property
    def case_xid(self):
        """
         The current Case xid for the artifact.
        """
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        """
        Sets the case xid for the Artifact
        """
        self._case_xid = case_xid

    @property
    def file_data(self):
        """
        Returns the File Data for the Artifact
        """
        return self._file_data

    @file_data.setter
    def file_data(self, file_data):
        """
        Sets the File Data for the Artifact
        """
        self._file_data = file_data

    @property
    def intel_type(self):
        """
        Returns the Intel Type for the Artifact
        """
        return self._intel_type

    @intel_type.setter
    def intel_type(self, intel_type):
        """
        Sets the Intel Type for the Artifact
        """
        self._intel_type = intel_type

    @property
    def notes(self):
        """
        Returns the Notes for the Artifact
        """
        return self._notes

    @notes.setter
    def notes(self, notes):
        """
        Sets the Notes for the Artifact
        """
        self._notes = notes

    @property
    def source(self):
        """
        Returns the Source for the Artifact
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        Sets the Source of the Artifact
        """
        self._source = source

    @property
    def summary(self):
        """
        Returns the Summary for the Artifact
        """
        return self._summary

    @summary.setter
    def summary(self, summary):
        """
        Sets the Summary for the Artifact
        """
        self._summary = summary

    @property
    def task_id(self):
        """
        Returns the Task ID for the Artifact
        """
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """
        Sets the Task ID for the Artifact
        """
        self._task_id = task_id

    @property
    def task_xid(self):
        """
        Returns the Task xid for the Artifact
        """
        return self._task_id

    @task_xid.setter
    def task_xid(self, task_xid):
        """
        Sets the Task xid for the Artifact
        """
        self._task_id = task_xid

    @property
    def date_added(self):
        """
        Returns the Date Added for the Artifact
        """
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """
        Sets the Date Added for the Artifact
        """
        self._date_added = date_added

    @property
    def type(self):
        """
        Returns the Artifact Type for the Artifact
        """
        return self._type

    @type.setter
    def type(self, artifact_type):
        """
        Sets the Artifact Type for the Artifact
        """
        self._type = artifact_type
