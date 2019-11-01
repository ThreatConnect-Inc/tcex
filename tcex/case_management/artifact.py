# -*- coding: utf-8 -*-
from .artifact_type import ArtifactType
from .note import Note, Notes
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL

api_endpoint = '/v3/artifacts'


class Artifacts(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)
        self.tql = TQL()
        self.added_artifacts = []

    def summary_filter(self, operator, summary):
        """
            The summary of the artifact
        """
        self.tql.add_filter('summary', operator, summary)

    def case_id_filter(self, operator, case_id):
        """
            The ID of the case associated with this artifact
        """
        self.tql.add_filter('caseid', operator, case_id)

    def comment_id_filter(self, operator, comment_id):
        """
            The ID of the comment associated with this artifact
        """
        self.tql.add_filter('commentid', operator, comment_id)

    def id_filter(self, operator, id):
        """
            The ID of the artifact
        """
        self.tql.add_filter('id', operator, id)

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
        self.tql.add_filter('taskid', operator, task_id)

    def type_name_filter(self, operator, type_name):
        """
            The type name of the artifact
        """
        self.tql.add_filter('typename', operator, type_name)

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return Artifact(self.tcex, **entity)
    
    def add_artifact(self, artifact):
        self.added_artifacts.append(artifact)

    @property
    def as_dict(self):
        return super().as_dict(self.added_artifacts)


class Artifact(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, **kwargs)
        self._case_id = kwargs.get('case_id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._file_data = kwargs.get('file_data', None)
        self._intel_type = kwargs.get('intel_type', None)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}).get('data'))
        self._source = kwargs.get('source', None)
        self._summary = kwargs.get('summary', None)
        self._task_id = kwargs.get('task_id', None)
        self._task_xid = kwargs.get('task_xid', None)
        self._type = ArtifactType(kwargs.get('type', None))
        self._xid = None

    def add_note(self, **kwargs):
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def required_properties(self):
        return ['summary', 'type', 'intel_type', 'case_id']

    @property
    def available_fields(self):
        return [
            'caseXid', 'caseId',
            'fileData', 'intelType',
            'notes', 'source',
            'summary', 'taskId',
            'taskXid'
        ]

    @property
    def xid(self):
        return self._xid

    @xid.setter
    def xid(self, xid):
        self._xid = xid

    @property
    def notes(self):
        return self._notes

    @property
    def case_id(self):
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        self._case_id = case_id

    @property
    def case_xid(self):
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        self._case_xid = case_xid

    @property
    def file_data(self):
        return self._file_data

    @file_data.setter
    def file_data(self, file_data):
        self._file_data = file_data

    @property
    def intel_type(self):
        return self._intel_type

    @intel_type.setter
    def intel_type(self, intel_type):
        self._intel_type = intel_type

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, notes):
        self._notes = notes

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._source = source

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        self._summary = summary

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        self._task_id = task_id

    @property
    def task_xid(self):
        return self._task_id

    @task_xid.setter
    def task_xid(self, task_xid):
        self._task_id = task_xid

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, artifact_type):
        self._type = artifact_type
