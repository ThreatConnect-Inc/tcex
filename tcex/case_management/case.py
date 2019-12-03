# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .artifact import Artifact, Artifacts
from .task import Task, Tasks
from .note import Note, Notes
from .tag import Tag, Tags
from .tql import TQL

api_endpoint = '/v3/cases'


class Cases(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None, tql_filters=None):
        super().__init__(tcex, api_endpoint, initial_response=initial_response,
                         tql_filters=tql_filters)
        self.tql = TQL()

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def severity_filter(self, operator, severity):
        """
            The severity of the case
        """
        self.tql.add_filter('severity', operator, severity)

    def target_id_filter(self, operator, target_id):
        """
            The assigned user or group ID for the case
        """
        self.tql.add_filter('targetid', operator, target_id)

    def target_type_filter(self, operator, target_type):
        """
            The target type for this case (either User or Group)
        """
        self.tql.add_filter('targettype', operator, target_type)

    def tag_filter(self, operator, tag):
        """
            A nested query for association to labels
        """
        self.tql.add_filter('hastag', operator, tag)

    def owner_name_filter(self, operator, owner_name):
        """
            The name of the case owner
        """
        self.tql.add_filter('ownername', operator, owner_name)

    def task_filter(self, operator, task):
        """
            A nested query for association to tasks
        """
        self.tql.add_filter('hastask', operator, task)

    def description_filter(self, operator, description):
        """
            The description of the case
        """
        self.tql.add_filter('description', operator, description)

    def created_by_id_filter(self, operator, created_by_id):
        """
            The user ID for the creator of the case
        """
        self.tql.add_filter('createdbyid', operator, created_by_id)

    def resolution_filter(self, operator, resolution):
        """
            The resolution of the case
        """
        self.tql.add_filter('resolution', operator, resolution)

    def artifact_filter(self, operator, artifact):
        """
            A nested query for association to artifacts
        """
        self.tql.add_filter('hasartifact', operator, artifact)

    def xid_filter(self, operator, xid):
        """
            The XID of the case
        """
        self.tql.add_filter('xid', operator, xid)

    def name_filter(self, operator, name):
        """
            The name of the case
        """
        self.tql.add_filter('name', operator, name)

    def id_filter(self, operator, id):
        """
            The ID of the case
        """
        self.tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    #What is the difference between this and hastag?
    def tag_filter(self, operator, tag):
        """
            The name of a tag applied to a case
        """
        self.tql.add_filter('tag', operator, tag)

    def status_filter(self, operator, status):
        """
            The status of the case
        """
        self.tql.add_filter('status', operator, status)

    def entity_map(self, entity):
        return Case(self.tcex, **entity)


class Case(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, kwargs)
        case_filter = [{'keyword': 'caseid', 'operator': '=', 'value': self.id, 'type': 'integer'}]

        self._name = kwargs.get('name', None)
        self._severity = kwargs.get('severity', None)
        self._status = kwargs.get('status', None)
        self._date_added = kwargs.get('date_added', None)
        self._resolution = kwargs.get('resolution', None)
        self._created_by = Creator(**kwargs.get('created_by', {}))
        self._tasks = Tasks(self.tcex, kwargs.get('tasks', {}), tql_filters=case_filter)
        self._artifacts = Artifacts(self.tcex, kwargs.get('artifacts', None), tql_filters=case_filter)
        self._tags = Tags(self.tcex, kwargs.get('tags', {}), tql_filters=case_filter)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}), tql_filters=case_filter)

    def entity_mapper(self, entity):
        new_case = Case(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def available_fields(self):
        return ['artifacts', 'events', 'notes', 'related', 'tags', 'tasks']

    def add_tag(self, **kwargs):
        self._tags.add_tag(Tag(self.tcex, **kwargs))

    def add_note(self, **kwargs):
        self._notes.add_note(Note(self.tcex, **kwargs))

    def add_task(self, **kwargs):
        self._tasks.add_task(Task(self.tcex, **kwargs))

    def add_artifact(self, **kwargs):
        self._artifacts.add_artifact(Artifact(self.tcex, **kwargs))

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

    @property
    def date_added(self):
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        self._date_added = date_added


class Creator(object):
    def __init__(self, **kwargs):
        self._transform_kwargs(kwargs)
        self._id = kwargs.get('id', None)
        self._user_name = kwargs.get('user_name', None)
        self._first_name = kwargs.get('first_name', None)
        self._pseudonym = kwargs.get('pseudonym', None)
        self._role = kwargs.get('role', None)

    def _transform_kwargs(self, kwargs):
        for key, value in dict(kwargs).items():
            new_key = self._metadata_map.get(key, key)
            kwargs[new_key] = kwargs.pop(key)

    @property
    def _metadata_map(self):
        return {
            'dateAdded': 'date_added',
            'firstName': 'first_name',
            'userName': 'user_name',
        }

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

    @property
    def role(self):
        return self._pseudonym

    @role.setter
    def role(self, role):
        self._role = role
