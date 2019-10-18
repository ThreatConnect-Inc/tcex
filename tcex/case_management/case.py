# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .artifact import Artifact, Artifacts
from .task import Task, Tasks
from .note import Note, Notes
from .tag import Tag, Tags

api_endpoint = '/v3/cases'


class Cases(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return Case(self.tcex, **entity)


class Case(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, kwargs)
        self._name = kwargs.get('name', None)
        self._severity = kwargs.get('severity', None)
        self._status = kwargs.get('status', None)
        self._resolution = kwargs.get('resolution', None)
        self._created_by = Creator(**kwargs.get('created_by', {}))
        self._tasks = Tasks(self.tcex, kwargs.get('tasks', {}))
        self._artifacts = Artifacts(self.tcex, kwargs.get('artifacts', {}))
        self._tags = Tags(self.tcex, kwargs.get('tags', {}))
        self._notes = Notes(self.tcex, kwargs.get('notes', {}))

    def add_tag(self, **kwargs):
        self._tags.add_tag(Tag(self.tcex, **kwargs))

    def add_note(self, **kwargs):
        self._notes.add_note(Note(self.tcex, **kwargs))

    def add_task(self, **kwargs):
        self._tasks.add_task(Task(self.tcex, **kwargs))

    def add_artifact(self, **kwargs):
        self._artifacts.add_artifact(Artifact(self.tcex, **kwargs))

    def entity_mapper(self, entity):
        new_case = Case(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def required_properties(self):
        return ['status', 'severity', 'name']

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def severity(self):
        return self._severity

    @severity.setter
    def severity(self, artifact_severity):
        self._severity = artifact_severity

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        self._resolution = resolution

    @property
    def created_by(self):
        return self._created_by

    @created_by.setter
    def created_by(self, created_by):
        self._created_by = created_by

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, notes):
        self._notes = notes

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, tags):
        self._tags = tags

    @property
    def tasks(self):
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        self._tasks = tasks

    @property
    def artifacts(self):
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts):
        self._artifacts = artifacts


class Creator(object):
    def __init__(self, **kwargs):
        self._id = kwargs.get('id', None)
        self._user_name = kwargs.get('user_name', None)
        self._first_name = kwargs.get('first_name', None)
        self._pseudonym = kwargs.get('pseudonym', None)

    @property
    def as_dict(self):
        properties = vars(self)
        as_dict = {}
        for key, value in properties.items():
            key = key.lstrip('_')
            if value is None:
                continue
            as_dict[key] = value

        if not as_dict:
            return None

        return as_dict

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, creator_id):
        self._id = creator_id

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        self._user_name = user_name

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        self._first_name = first_name

    @property
    def pseudonym(self):
        return self._pseudonym

    @pseudonym.setter
    def pseudonym(self, pseudonym):
        self._pseudonym = pseudonym
