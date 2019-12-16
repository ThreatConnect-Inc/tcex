# -*- coding: utf-8 -*-
"""ThreatConnect Task"""
from .note import Note, Notes
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL

api_endpoint = '/v3/tasks'


class Tasks(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None, tql_filters=None):
        super().__init__(
            tcex, api_endpoint, initial_response=initial_response, tql_filters=tql_filters
        )
        self.added_tasks = []

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def target_id_filter(self, operator, target_id):
        """
            The target_id of the artifact
        """
        self.tql.add_filter('targetid', operator, target_id)

    def target_type_filter(self, operator, target_type):
        """
            The ID of the description associated with this artifact
        """
        self.tql.add_filter('targettype', operator, target_type)

    def intel_type_filter(self, operator, intel_type):
        """
            The ID of the comment associated with this artifact
        """
        self.tql.add_filter('inteltype', operator, intel_type)

    def id_filter(self, operator, id):
        """
            The ID of the artifact
        """
        self.tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name_filter(self, operator, name):
        """
            The name of the artifact
        """
        self.tql.add_filter('name', operator, name)

    def description_filter(self, operator, description):
        """
            A nested query for association to other descriptions
        """
        self.tql.add_filter('description', operator, description)

    def config_playbook_filter(self, operator, config_playbook):
        """
            The ID of the task associated with this artifact
        """
        self.tql.add_filter('configplaybook', operator, config_playbook)

    def duration_filter(self, operator, duration):
        """
            The type name of the artifact
        """
        self.tql.add_filter('duration', operator, duration)

    def xid_filter(self, operator, xid):
        """
            The type name of the artifact
        """
        self.tql.add_filter('xid', operator, xid)

    def due_date_filter(self, operator, due_date):
        """
            The type name of the artifact
        """
        self.tql.add_filter('duedate', operator, due_date)

    def case_id_filter(self, operator, case_id):
        """
            The type name of the artifact
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def config_task_filter(self, operator, config_task):
        """
            The type name of the artifact
        """
        self.tql.add_filter('configtask', operator, config_task)

    def case_filter(self, operator, case):
        """
            The type name of the artifact
        """
        self.tql.add_filter('hascase', operator, case)

    def completed_date_filter(self, operator, completed_date):
        """
            The type name of the artifact
        """
        self.tql.add_filter('completeddate', operator, completed_date)

    def status_filter(self, operator, status):
        """
            The type name of the artifact
        """
        self.tql.add_filter('status', operator, status)

    def entity_map(self, entity):
        return Task(self.tcex, **entity)

    def add_task(self, tag):
        self.added_tasks.append(tag)

    @property
    def as_dict(self):
        return super().list_as_dict(self.added_tasks)


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
        self._source = kwargs.get('source', None)
        self._notes = Notes(kwargs.get('notes', {}).get('data'))

    def add_note(self, **kwargs):
        """
        Adds a note to the task
        """
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def required_properties(self):
        """
        The required fields for a task
        Returns:
            list of required fields for a task.
        """
        return ['name', 'case_id']

    def entity_mapper(self, entity):
        """
         Maps a dict to a Task then updates self.

         Args:
             entity (dict): The dict to map self too.
         """
        new_case = Task(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def available_fields(self):
        """
        The available fields to fetch for the task.
        Returns:
            list of available fields to fetch for the task.
        """
        return ['artifacts', 'assignee', 'caseId', 'notes', 'parentCase']

    @property
    def name(self):
        """
         Returns the name for the Task
         """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name for the Task
        """
        self._name = name

    @property
    def case_id(self):
        """
        Returns the case id for the Task
        """
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """
        Sets the case id for the Task
        """
        self._case_id = case_id

    @property
    def description(self):
        """
        Returns the description for the Task
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description for the Task
        """
        self._description = description

    @property
    def is_workflow(self):
        """
        Returns if the Task is part of a workflow.
        """
        return self._is_workflow

    @is_workflow.setter
    def is_workflow(self, is_workflow):
        """
        Sets if the Task is part of a workflow.
        """
        self._is_workflow = is_workflow

    @property
    def workflow_id(self):
        """
        Returns the workflow id for the Task
        """
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, workflow_id):
        """
        Sets the workflow id for the Task
        """
        self._workflow_id = workflow_id

    @property
    def notes(self):
        """
        Returns the notes for the Task
        """
        return self._notes

    @notes.setter
    def notes(self, notes):
        """
        Sets the notes for the Task
        """
        self._notes = notes

    @property
    def source(self):
        """
        Returns the source for the Task
        """
        return self._source

    @source.setter
    def source(self, source):
        """
        Sets the source for the Task
        """
        self._source = source

    @property
    def workflow_phase(self):
        """
        Returns the workflow phase for the Task
        """
        return self._workflow_phase

    @workflow_phase.setter
    def workflow_phase(self, workflow_phase):
        """
        Sets the workflow phase for the Task
        """
        self._workflow_phase = workflow_phase

    @property
    def workflow_step(self):
        """
        Returns the workflow step for the Task
        """
        return self._workflow_step

    @workflow_step.setter
    def workflow_step(self, workflow_step):
        """
        Sets the workflow step for the Task
        """
        self._workflow_step = workflow_step

    @property
    def status(self):
        """
        Returns the status for the Task
        """
        return self._status

    @status.setter
    def status(self, status):
        """
        Sets the status for the Task
        """
        self._status = status

    # @property
    # def type(self):
    #     """
    #     Returns the type for the Task
    #     """
    #     return self._type
    #
    # @type.setter
    # def type(self, artifact_type):
    #     """
    #     Sets the type for the Task
    #     """
    #     self._type = artifact_type
