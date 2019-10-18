# -*- coding: utf-8 -*-
from .note import Note, Notes
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection

api_endpoint = 'v3/artifacts'


class Tasks(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)
        self.added_tasks = []

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return Task(self.tcex, **entity)

    def add_task(self, tag):
        self.added_tasks.append(tag)

    @property
    def as_dict(self):
        return super().as_dict(self.added_tasks)


class Task(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, kwargs)
        self._case_id = kwargs.get('case_id', None)
        self._name = kwargs.get('name', None)
        self._description = kwargs.get('description', None)
        self._is_workflow = kwargs.get('is_workflow', None)
        self._workflow_id = kwargs.get('workflow_id', None)
        self._workflow_phase = kwargs.get('workflow_phase', None)
        self._workflow_step = kwargs.get('workflow_step', None)
        self._status = kwargs.get('status', None)
        self._notes = Notes(kwargs.get('notes', {}).get('data'))

    def add_note(self, **kwargs):
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

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
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def is_workflow(self):
        return self._is_workflow

    @is_workflow.setter
    def is_workflow(self, is_workflow):
        self._is_workflow = is_workflow

    @property
    def workflow_id(self):
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, workflow_id):
        self._workflow_id = workflow_id

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
    def workflow_phase(self):
        return self._workflow_phase

    @workflow_phase.setter
    def workflow_phase(self, workflow_phase):
        self._workflow_phase = workflow_phase

    @property
    def workflow_step(self):
        return self._workflow_step

    @workflow_step.setter
    def workflow_step(self, workflow_step):
        self._workflow_step = workflow_step

    @property
    def status(self):
        return self._workflow_step

    @status.setter
    def status(self, status):
        self._workflow_step = status

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, artifact_type):
        self._type = artifact_type
