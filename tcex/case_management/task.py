# -*- coding: utf-8 -*-
"""ThreatConnect Task"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .note import Note, Notes
from .tql import TQL


class Tasks(CommonCaseManagementCollection):
    """[summary]

    Args:
        tcex ([type]): [description]
        initial_response ([type], optional): [description]. Defaults to None.
        tql_filters ([type], optional): [description]. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties."""
        super().__init__(
            tcex, ApiEndpoints.TASKS, initial_response=initial_response, tql_filters=tql_filters
        )
        self.added_tasks = []

    def __iter__(self):
        """Iterate on Tasks"""
        return self.iterate(initial_response=self.initial_response)

    def target_id_filter(self, operator, target_id):
        """[summary]

        Args:
            operator ([type]): [description]
            target_id ([type]): [description]
        """
        self.tql.add_filter('targetid', operator, target_id)

    def target_type_filter(self, operator, target_type):
        """[summary]

        Args:
            operator ([type]): [description]
            target_type ([type]): [description]
        """
        self.tql.add_filter('targettype', operator, target_type)

    def intel_type_filter(self, operator, intel_type):
        """[summary]

        Args:
            operator ([type]): [description]
            intel_type ([type]): [description]
        """
        self.tql.add_filter('inteltype', operator, intel_type)

    def id_filter(self, operator, id_):
        """[summary]

        Args:
            operator ([type]): [description]
            id_ ([type]): [description]
        """
        self.tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def name_filter(self, operator, name):
        """[summary]

        Args:
            operator ([type]): [description]
            name ([type]): [description]
        """
        self.tql.add_filter('name', operator, name)

    def description_filter(self, operator, description):
        """[summary]

        Args:
            operator ([type]): [description]
            description ([type]): [description]
        """
        self.tql.add_filter('description', operator, description)

    def config_playbook_filter(self, operator, config_playbook):
        """[summary]

        Args:
            operator ([type]): [description]
            config_playbook ([type]): [description]
        """
        self.tql.add_filter('configplaybook', operator, config_playbook)

    def duration_filter(self, operator, duration):
        """[summary]

        Args:
            operator ([type]): [description]
            duration ([type]): [description]
        """
        self.tql.add_filter('duration', operator, duration)

    def xid_filter(self, operator, xid):
        """[summary]

        Args:
            operator ([type]): [description]
            xid ([type]): [description]
        """
        self.tql.add_filter('xid', operator, xid)

    def due_date_filter(self, operator, due_date):
        """[summary]

        Args:
            operator ([type]): [description]
            due_date ([type]): [description]
        """
        self.tql.add_filter('duedate', operator, due_date)

    def case_id_filter(self, operator, case_id):
        """[summary]

        Args:
            operator ([type]): [description]
            case_id ([type]): [description]
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def config_task_filter(self, operator, config_task):
        """[summary]

        Args:
            operator ([type]): [description]
            config_task ([type]): [description]
        """
        self.tql.add_filter('configtask', operator, config_task)

    def case_filter(self, operator, case):
        """[summary]

        Args:
            operator ([type]): [description]
            case ([type]): [description]
        """
        self.tql.add_filter('hascase', operator, case)

    def completed_date_filter(self, operator, completed_date):
        """[summary]

        Args:
            operator ([type]): [description]
            completed_date ([type]): [description]
        """
        self.tql.add_filter('completeddate', operator, completed_date)

    def status_filter(self, operator, status):
        """[summary]

        Args:
            operator ([type]): [description]
            status ([type]): [description]
        """
        self.tql.add_filter('status', operator, status)

    def entity_map(self, entity):
        """[summary]

        Args:
            entity ([type]): [description]

        Returns:
            [type]: [description]
        """
        return Task(self.tcex, **entity)

    def add_task(self, tag):
        """[summary]

        Args:
            tag ([type]): [description]
        """
        self.added_tasks.append(tag)

    @property
    def as_dict(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return super().list_as_dict(self.added_tasks)


class Task(CommonCaseManagement):
    """[summary]

    Args:
        tcex ([type]): [description]
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.TASKS, kwargs)
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
        """Adds a note to the task"""
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def required_properties(self):
        """Return the required fields for a task

        Returns:
            list: All required fields for a task.
        """
        return ['name', 'case_id']

    def entity_mapper(self, entity):
        """Maps a dict to a Task then updates self.

        Args:
            entity (dict): The dict to map self too.
        """
        new_case = Task(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def available_fields(self):
        """Return the available fields to fetch for the task.

        Returns:
            list: All available fields to fetch for the task.
        """
        return ['artifacts', 'assignee', 'caseId', 'notes', 'parentCase']

    @property
    def name(self):
        """Return the name for the Task"""
        return self._name

    @name.setter
    def name(self, name):
        """Set the name for the Task"""
        self._name = name

    @property
    def case_id(self):
        """Return the case id for the Task"""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the case id for the Task"""
        self._case_id = case_id

    @property
    def description(self):
        """Return the description for the Task"""
        return self._description

    @description.setter
    def description(self, description):
        """Set the description for the Task"""
        self._description = description

    @property
    def is_workflow(self):
        """Return if the Task is part of a workflow"""
        return self._is_workflow

    @is_workflow.setter
    def is_workflow(self, is_workflow):
        """Set if the Task is part of a workflow"""
        self._is_workflow = is_workflow

    @property
    def workflow_id(self):
        """Return the workflow id for the Task"""
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, workflow_id):
        """Set the workflow id for the Task"""
        self._workflow_id = workflow_id

    @property
    def notes(self):
        """Return the notes for the Task"""
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the notes for the Task"""
        self._notes = notes

    @property
    def source(self):
        """Return the source for the Task"""
        return self._source

    @source.setter
    def source(self, source):
        """Set the source for the Task"""
        self._source = source

    @property
    def workflow_phase(self):
        """Return the workflow phase for the Task"""
        return self._workflow_phase

    @workflow_phase.setter
    def workflow_phase(self, workflow_phase):
        """Set the workflow phase for the Task"""
        self._workflow_phase = workflow_phase

    @property
    def workflow_step(self):
        """Return the workflow step for the Task"""
        return self._workflow_step

    @workflow_step.setter
    def workflow_step(self, workflow_step):
        """Set the workflow step for the Task"""
        self._workflow_step = workflow_step

    @property
    def status(self):
        """Return the status for the Task"""
        return self._status

    @status.setter
    def status(self, status):
        """Set the status for the Task"""
        self._status = status

    # @property
    # def type(self):
    #     """Return the type for the Task"""
    #     return self._type

    # @type.setter
    # def type(self, artifact_type):
    #     """Set the type for the Task"""
    #     self._type = artifact_type
