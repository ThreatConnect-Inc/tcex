# -*- coding: utf-8 -*-
from .note import Note, Notes
from .artifact_type import ArtifactType
from .note import Note
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection

api_endpoint = 'v3/artifacts'


class Artifacts(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return Artifact(self.tcex, **entity)


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

    def note(self, **kwargs):
        note = Note(**kwargs)
        self.notes.append(note)
        return Note

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
