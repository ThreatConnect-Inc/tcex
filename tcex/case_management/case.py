# -*- coding: utf-8 -*-
"""ThreatConnect Case"""
from .artifact import Artifact, Artifacts
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .note import Note, Notes
from .tag import Tag, Tags
from .task import Task, Tasks
from .tql import TQL

api_endpoint = '/v3/cases'


class Cases(CommonCaseManagementCollection):
    """ A iterable class to fetch Artifact Types"""

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

    def __iter__(self):
        """
        Iterates over the artifacts using the provided or applied tql filters.
        """
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

    def id_filter(self, operator, case_id):
        """
            The ID of the case
        """
        self.tql.add_filter('id', operator, case_id, TQL.Type.INTEGER)

    def status_filter(self, operator, status):
        """
            The status of the case
        """
        self.tql.add_filter('status', operator, status)

    def entity_map(self, entity):
        return Case(self.tcex, **entity)


class Case(CommonCaseManagement):
    """Unique API calls for Artifact Type API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """
           Initializes the Artifacts class:
           Args:
               tcex:
               name (str): The name for the case.
               severity (str): The severity for the case.
               status (str): The status for the case.
               date_added (date): The date added for the case.
               resolution (string): The resolution for the case.
               created_by (dict): The person created by for the case.
               tasks (dict): The tasks for the case.
               artifacts (dict): The artifacts for the case.
               tags (dict): The tags for the case.
               notes (dict): The notes for the case.
       """
        super().__init__(tcex, api_endpoint, kwargs)
        case_filter = [
            {'keyword': 'caseid', 'operator': TQL.Operator.EQ, 'value': self.id, 'type': 'integer'}
        ]

        self._name = kwargs.get('name', None)
        self._severity = kwargs.get('severity', None)
        self._status = kwargs.get('status', None)
        self._date_added = kwargs.get('date_added', None)
        self._resolution = kwargs.get('resolution', None)
        self._created_by = Creator(**kwargs.get('created_by', {}))
        self._tasks = Tasks(self.tcex, kwargs.get('tasks', {}), tql_filters=case_filter)
        self._artifacts = Artifacts(
            self.tcex, kwargs.get('artifacts', None), tql_filters=case_filter
        )
        self._tags = Tags(self.tcex, kwargs.get('tags', {}), tql_filters=case_filter)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}), tql_filters=case_filter)

    def entity_mapper(self, entity):
        """
         Maps a dict to a Case then updates self.

         Args:
             entity (dict): The dict to map self too.
         """
        new_case = Case(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def available_fields(self):
        """
         The available fields to fetch for the Case.
         Returns:
             list of available fields to fetch for the Case.
         """
        return ['artifacts', 'events', 'notes', 'related', 'tags', 'tasks']

    def add_tag(self, **kwargs):
        """Stages a tag to be added to the Case."""
        self._tags.add_tag(Tag(self.tcex, **kwargs))

    def add_note(self, **kwargs):
        """Stages a note to be added to the Case."""
        self._notes.add_note(Note(self.tcex, **kwargs))

    def add_task(self, **kwargs):
        """Stages a task to be added to the Case."""
        self._tasks.add_task(Task(self.tcex, **kwargs))

    def add_artifact(self, **kwargs):
        """Stages a artifact to be added to the Case."""
        self._artifacts.add_artifact(Artifact(self.tcex, **kwargs))

    @property
    def required_properties(self):
        """
         The required fields for a Case
         Returns:
             list of required fields for a Case.
         """
        return ['status', 'severity', 'name']

    @property
    def name(self):
        """
        Returns the name for the Case.
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name for the Case.
        """
        self._name = name

    @property
    def severity(self):
        """
        Returns the severity for the Case.
        """
        return self._severity

    @severity.setter
    def severity(self, artifact_severity):
        """
        Sets the severity for the Case.
        """
        self._severity = artifact_severity

    @property
    def status(self):
        """
        Returns the status for the Case.
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status for the Case.
        """
        self._status = status

    @property
    def resolution(self):
        """
        Returns the resolution for the Case.
        """
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """
        Sets the resolution for the Case.
        """
        self._resolution = resolution

    @property
    def created_by(self):
        """
        Returns the creator for the Case.
        """
        return self._created_by

    @created_by.setter
    def created_by(self, created_by):
        """
        Sets the creator for the Case.
        """
        self._created_by = created_by

    @property
    def notes(self):
        """
        Returns the notes for the Case.
        """
        return self._notes

    @notes.setter
    def notes(self, notes):
        """
        Sets the notes for the Case.
        """
        self._notes = notes

    @property
    def tags(self):
        """
        Returns the tags for the Case.
        """
        return self._tags

    @tags.setter
    def tags(self, tags):
        """
        Sets the tags for the Case.
        """
        self._tags = tags

    @property
    def tasks(self):
        """
        Returns the tasks for the Case.
        """
        return self._tasks

    @tasks.setter
    def tasks(self, tasks):
        """
        Sets the tasks for the Case.
        """
        self._tasks = tasks

    @property
    def artifacts(self):
        """
        Returns the artifacts for the Case.
        """
        return self._artifacts

    @artifacts.setter
    def artifacts(self, artifacts):
        """
        Sets the artifacts for the Case.
        """
        self._artifacts = artifacts

    @property
    def date_added(self):
        """
        Returns the date added for the Case.
        """
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """
        Sets the date added for the Case.
        """
        self._date_added = date_added


class Creator:
    """ Sub class of the Cases object. Used to map the creator to."""

    def __init__(self, **kwargs):
        """
           Initializes the Creator class:
           Args:
               tcex:
               id (id): The id of the creator.
               user_name (str): The user name of the creator.
               first_name (str): The first name of the creator.
               pseudonym (str): The pseudonym of the creator.
               role (str): The role of the creator.
        """
        self._transform_kwargs(kwargs)
        self._id = kwargs.get('id', None)
        self._user_name = kwargs.get('user_name', None)
        self._first_name = kwargs.get('first_name', None)
        self._pseudonym = kwargs.get('pseudonym', None)
        self._role = kwargs.get('role', None)

    def _transform_kwargs(self, kwargs):
        """
        Maps the provided kwargs to expected arguments.
        """
        for key in dict(kwargs):
            new_key = self._metadata_map.get(key, key)
            kwargs[new_key] = kwargs.pop(key)

    @property
    def _metadata_map(self):
        """ Returns a mapping of kwargs to expected args. """
        return {'dateAdded': 'date_added', 'firstName': 'first_name', 'userName': 'user_name'}

    @property
    def as_dict(self):
        """
        Returns a dict representation of the Creator class.
        """
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
        """
        Returns the id for the Creator.
        """
        return self._id

    @id.setter
    def id(self, creator_id):
        """
        Sets the id for the Creator.
        """
        self._id = creator_id

    @property
    def user_name(self):
        """
        Returns the user name for the Creator.
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """
        Sets the user name for the Creator.
        """
        self._user_name = user_name

    @property
    def first_name(self):
        """
        Returns the first name for the Creator.
        """
        return self._first_name

    @first_name.setter
    def first_name(self, first_name):
        """
        Sets the first name for the Creator.
        """
        self._first_name = first_name

    @property
    def pseudonym(self):
        """
        Returns the pseudonym for the Creator.
        """
        return self._pseudonym

    @pseudonym.setter
    def pseudonym(self, pseudonym):
        """
        Sets the pseudonym for the Creator.
        """
        self._pseudonym = pseudonym

    @property
    def role(self):
        """
        Returns the role for the Creator.
        """
        return self._pseudonym

    @role.setter
    def role(self, role):
        """
        Sets the role for the Creator.
        """
        self._role = role
