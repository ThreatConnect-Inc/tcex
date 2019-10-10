# -*- coding: utf-8 -*-
from .notes import Notes
from .artifact_type import ArtifactType
from .note import Note


class Artifact(object):
    def __init__(self, entity=None):
        if entity is None:
            entity = {}
        self._case_id = entity.get('caseId', None)
        self._case_xid = entity.get('caseId', None)
        self._file_data = entity.get('caseId', None)
        self._intel_type = entity.get('caseId', None)
        self._notes = Notes(entity.get('notes', {}).get('data'))
        self._source = entity.get('source', None)
        self._summary = entity.get('summary', None)
        self._task_id = entity.get('taskId', None)
        self._task_xid = entity.get('taskXid', None)
        self._type = ArtifactType(entity.get('type', None))

    def note(self, **kwargs):
        note = Note(**kwargs)
        self.notes.append(note)
        return Note

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
