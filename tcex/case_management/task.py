# -*- coding: utf-8 -*-
"""ThreatConnect Task"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .note import Note, Notes
from .tql import TQL


class Tasks(CommonCaseManagementCollection):
    """Tasks Class for Case Management Collection

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties."""
        super().__init__(
            tcex, ApiEndpoints.TASKS, initial_response=initial_response, tql_filters=tql_filters
        )
        self.added_tasks = []

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def add_task(self, task):
        """Add an task to a case.

        Args:
            task (Task): The Task Object to add.
        """
        self.added_tasks.append(task)

    @property
    def as_dict(self):
        """Return a dict version of this object."""
        return super().list_as_dict(self.added_tasks)

    def entity_map(self, entity):
        """Map a dict to a Task.

        Args:
            entity (dict): The Task data.

        Returns:
            CaseManagement.Task: An Task Object
        """
        return Task(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterArtifact Object."""
        return FilterTask(self.tql)


class Task(CommonCaseManagement):
    """Artifact object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        case_id (int, kwargs): The Case ID for the Task.
        case_xid (str, kwargs): The unique Case XID for the Task.
        description (str, kwargs): The Description for the Task.
        is_workflow (bool, kwargs): The Is Workflow for the Task.
        name (str, kwargs): The Name for the Task.
        notes (dict, kwargs): The Notes for the Task.
        source (str, kwargs): The Source for the Task.
        workflow_id (str, kwargs): The Workflow ID for the Task.
        workflow_phase (str, kwargs): The Workflow Phase for the Task.
        workflow_step (str, kwargs): The Workflow Step for the Task.
        xid (str, kwargs): The unique XID for the Task.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.TASKS, kwargs)

        self._case_id = kwargs.get('case_id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._description = kwargs.get('description', None)
        self._is_workflow = kwargs.get('is_workflow', None)
        self._name = kwargs.get('name', None)
        self._notes = Notes(kwargs.get('notes', {}).get('data'))
        self._source = kwargs.get('source', None)
        self._status = kwargs.get('status', None)
        self._workflow_id = kwargs.get('workflow_id', None)
        self._workflow_phase = kwargs.get('workflow_phase', None)
        self._workflow_step = kwargs.get('workflow_step', None)
        self._xid = kwargs.get('xid', None)

    def add_note(self, **kwargs):
        """Add a note to the task"""
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def as_entity(self):
        """Return the entity representation of the Artifact."""
        return {'type': 'Task', 'value': self.name, 'id': self.id}

    @property
    def available_fields(self):
        """Return the available fields to fetch for an Artifact."""
        return ['artifacts', 'assignee', 'caseId', 'notes', 'parentCase']

    @property
    def case_id(self):
        """Return the "Case ID" for the Task"""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the "Case ID" for the Task"""
        self._case_id = case_id

    @property
    def description(self):
        """Return the "Description" for the Task"""
        return self._description

    @description.setter
    def description(self, description):
        """Set the "Description" for the Task"""
        self._description = description

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): The dict to map self too.
        """
        new_case = Task(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def is_workflow(self):
        """Return the "Is Workflow" for the Task"""
        return self._is_workflow

    @is_workflow.setter
    def is_workflow(self, is_workflow):
        """Set the "Is Workflow" for the Task"""
        self._is_workflow = is_workflow

    @property
    def name(self):
        """Return the "Name" for the Task"""
        return self._name

    @name.setter
    def name(self, name):
        """Set the "Name" for the Task"""
        self._name = name

    @property
    def notes(self):
        """Return the "Notes" for the Task"""
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the "Notes" for the Task"""
        self._notes = notes

    @property
    def required_properties(self):
        """Return a list of required fields for an Artifact."""
        return ['name', 'case_id']

    @property
    def source(self):
        """Return the "Source" for the Task"""
        return self._source

    @source.setter
    def source(self, source):
        """Set the "Source" for the Task"""
        self._source = source

    @property
    def status(self):
        """Return the "Status" for the Task"""
        return self._status

    @status.setter
    def status(self, status):
        """Set the "Status" for the Task"""
        self._status = status

    @property
    def workflow_id(self):
        """Return the "Workflow ID" for the Task"""
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, workflow_id):
        """Set the "Workflow ID" for the Task"""
        self._workflow_id = workflow_id

    @property
    def workflow_phase(self):
        """Return the "Workflow Phase" for the Task"""
        return self._workflow_phase

    @workflow_phase.setter
    def workflow_phase(self, workflow_phase):
        """Set the "Workflow Phase" for the Task"""
        self._workflow_phase = workflow_phase

    @property
    def workflow_step(self):
        """Return the "Workflow Step" for the Task"""
        return self._workflow_step

    @workflow_step.setter
    def workflow_step(self, workflow_step):
        """Set the "Workflow Step" for the Task"""
        self._workflow_step = workflow_step


class FilterTask:
    """Filter Object for Task

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self.tql = tql

    def case(self, operator, case):
        """Filter objects based on "case" association.

        Args:
            operator (enum): The enum for the required operator.
            case (str): The filter value.
        """
        self.tql.add_filter('hascase', operator, case)

    def case_id(self, operator, case_id):
        """Filter objects based on "case id" field.

        Args:
            operator (enum): The enum for the required operator.
            case_id (int): The filter value.
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def completed_date(self, operator, completed_date):
        """Filter objects based on "completed date" field.

        Args:
            operator (enum): The enum for the required operator.
            completed_date (str): The filter value.
        """
        self.tql.add_filter('completeddate', operator, completed_date)

    def config_playbook(self, operator, config_playbook):
        """Filter objects based on "config playbook" field.

        Args:
            operator (enum): The enum for the required operator.
            config_playbook (str): The filter value.
        """
        self.tql.add_filter('configplaybook', operator, config_playbook)

    def config_task(self, operator, config_task):
        """Filter objects based on "config task" field.

        Args:
            operator (enum): The enum for the required operator.
            config_task (str): The filter value.
        """
        self.tql.add_filter('configtask', operator, config_task)

    def description(self, operator, description):
        """Filter objects based on "description" field.

        Args:
            operator (enum): The enum for the required operator.
            description (str): The filter value.
        """
        self.tql.add_filter('description', operator, description)

    def due_date(self, operator, due_date):
        """Filter objects based on "due date" field.

        Args:
            operator (enum): The enum for the required operator.
            due_date (str): The filter value.
        """
        self.tql.add_filter('duedate', operator, due_date)

    def duration(self, operator, duration):
        """Filter objects based on "duration" field.

        Args:
            operator (enum): The enum for the required operator.
            duration (str): The filter value.
        """
        self.tql.add_filter('duration', operator, duration)

    def id(self, operator, id_):
        """Filter objects based on "id" field.

        Args:
            operator (enum): The enum for the required operator.
            id (int): The filter value.
        """
        self.tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def intel_type(self, operator, intel_type):
        """Filter objects based on "intel type" field.

        Args:
            operator (enum): The enum for the required operator.
            intel_type (str): The filter value.
        """
        self.tql.add_filter('inteltype', operator, intel_type)

    def name(self, operator, name):
        """Filter objects based on "name" field.

        Args:
            operator (enum): The enum for the required operator.
            name (str): The filter value.
        """
        self.tql.add_filter('name', operator, name)

    def status(self, operator, status):
        """Filter objects based on "status" field.

        Args:
            operator (enum): The enum for the required operator.
            status (str): The filter value.
        """
        self.tql.add_filter('status', operator, status)

    def target_id(self, operator, target_id):
        """Filter objects based on "target id" field.

        Args:
            operator (enum): The enum for the required operator.
            target_id (str): The filter value.
        """
        self.tql.add_filter('targetid', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator, target_type):
        """Filter objects based on "target type" field.

        Args:
            operator (enum): The enum for the required operator.
            target_type (str): The filter value.
        """
        self.tql.add_filter('targettype', operator, target_type)

    def xid(self, operator, xid):
        """Filter objects based on "xid" field.

        Args:
            operator (enum): The enum for the required operator.
            xid (str): The filter value.
        """
        self.tql.add_filter('xid', operator, xid)
