# -*- coding: utf-8 -*-
"""ThreatConnect Task"""
from .assignee import Assignee
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class Tasks(CommonCaseManagementCollection):
    """Tasks Class for Case Management Collection

    params example: {
        'result_limit': 100, # How many results are retrieved.
        'result_start': 10,  # Starting point on retrieved results.
        'fields': ['caseId', 'summary'] # Additional fields returned on the results
    }

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Task. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Task objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.TASKS,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
        )

        if initial_response:
            for item in initial_response.get('data', []):
                self.added_items.append(Task(tcex, **item))

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def add_task(self, task):
        """Add an task to a case.

        Args:
            task (Task): The Task Object to add.
        """
        self.added_items.append(task)

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
        """Return instance of FilterWorkflowTemplate Object."""
        return FilterTasks(ApiEndpoints.TASKS, self.tcex, self.tql)


class Task(CommonCaseManagement):
    """Task object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        artifacts (Artifact, kwargs): a list of Artifacts corresponding to the Task
        assignee (Assignee, kwargs): the user or group Assignee object for the Task
        case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Task.
        case_xid (str, kwargs): [Required (alt: caseId)] The **Case Xid** for the Task.
        completed_by (str, kwargs): [Read-Only] The **Completed By** for the Task.
        completed_date (str, kwargs): the completion date of the Task
        config_playbook (str, kwargs): [Read-Only] The **Config Playbook** for the Task.
        config_task (dict, kwargs): [Read-Only] The **Config Task** for the Task.
        dependent_on_task_name (str, kwargs): [Read-Only] The **Dependent On Task Name** for the
            Task.
        description (str, kwargs): The **Description** for the Task.
        due_date (str, kwargs): the due date of the Task
        duration (int, kwargs): [Read-Only] The **Duration** for the Task.
        id_dependent_on (int, kwargs): [Read-Only] The **Id_Dependent On** for the Task.
        name (str, kwargs): [Required] The **Name** for the Task.
        notes (Note, kwargs): a list of Notes corresponding to the Task
        parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Task.
        required (bool, kwargs): [Read-Only] The **Required** flag for the Task.
        status (str, kwargs): The **Status** for the Task.
        workflow_phase (int, kwargs): the phase of the workflow
        workflow_step (int, kwargs): the step of the workflow
        xid (str, kwargs): The **Xid** for the Task.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.TASKS, kwargs)

        self._artifacts = kwargs.get('artifact', None)
        self._assignee = kwargs.get('assignee', None)
        self._case_id = kwargs.get('case_id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._completed_by = kwargs.get('completed_date', None)
        self._completed_date = kwargs.get('completed_date', None)
        self._config_playbook = kwargs.get('config_playbook', None)
        self._config_task = kwargs.get('config_task', None)
        self._dependent_on_task_name = kwargs.get('dependent_on_task_name', None)
        self._description = kwargs.get('description', None)
        self._due_date = kwargs.get('due_date', None)
        self._duration = kwargs.get('duration', None)
        self._id_dependent_on = kwargs.get('id_dependent_on', None)
        self._name = kwargs.get('name', None)
        self._notes = kwargs.get('notes', None)
        self._parent_case = kwargs.get('parent_case', None)
        self._required = kwargs.get('required', None)
        self._status = kwargs.get('status', None)
        self._workflow_phase = kwargs.get('workflow_phase', None)
        self._workflow_step = kwargs.get('workflow_step', None)
        self._xid = kwargs.get('xid', None)

    def add_note(self, **kwargs):
        """Add a note to the task"""
        self._notes.add_note(self.tcex.cm.note(**kwargs))

    @property
    def artifacts(self):
        """Return the **Artifacts** for the Task."""
        if self._artifacts:
            return self.tcex.cm.artifacts(initial_response=self._artifacts)
        return self._artifacts

    @property
    def as_entity(self):
        """Return the entity representation of the Task."""
        return {'type': 'Task', 'value': self.name, 'id': self.id}

    @property
    def assignee(self):
        """Return the **Assignee** for the Task."""
        if isinstance(self._assignee, dict):
            return self.tcex.cm.assignee(**self._assignee)
        return self._assignee

    @assignee.setter
    def assignee(self, assignee):
        """Set the **Assignee** for the Task."""
        if isinstance(assignee, dict):
            assignee = Assignee(type=assignee.get('type'), **assignee.get('data'))
        self._assignee = assignee

    @property
    def case_id(self):
        """Return the **Case ID** for the Task"""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the **Case ID** for the Task"""
        self._case_id = case_id

    @property
    def case_xid(self):
        """Return the **Case XID** for the Task"""
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        """Set the **Case XID** for the Task"""
        self._case_xid = case_xid

    @property
    def completed_by(self):
        """Return the **Completed By** for the Task"""
        return self._completed_by

    @property
    def completed_date(self):
        """Return the **Completed Date** for the Task"""
        return self._completed_date

    @completed_date.setter
    def completed_date(self, completed_date):
        """Set the **Completed Date** for the Task"""
        self._completed_date = completed_date

    @property
    def config_playbook(self):
        """Return the **Config Playbook** for the Task"""
        return self._config_playbook

    @property
    def config_task(self):
        """Return the **Config Task** for the Task"""
        return self._config_task

    @property
    def dependent_on_task_name(self):
        """Return the **Depend On Task Name** for the Task"""
        return self._dependent_on_task_name

    @property
    def description(self):
        """Return the **Description** for the Task"""
        return self._description

    @description.setter
    def description(self, description):
        """Set the **Description** for the Task"""
        self._description = description

    @property
    def due_date(self):
        """Return the **Due Date** for the Task"""
        return self._due_date

    @due_date.setter
    def due_date(self, due_date):
        """Set the **Completed Date** for the Task"""
        self._due_date = due_date

    @property
    def duration(self):
        """Return the **Duration** for the Task"""
        return self._duration

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = Task(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def id_dependent_on(self):
        """Return the **ID Dependent On** for the Task"""
        return self._id_dependent_on

    @property
    def name(self):
        """Return the **Name** for the Task"""
        return self._name

    @name.setter
    def name(self, name):
        """Set the **Name** for the Task"""
        self._name = name

    @property
    def notes(self):
        """Return the **Notes** for the Task"""
        if self._notes:
            return self.tcex.cm.notes(initial_response=self._notes)
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the **Notes** for the Task"""
        self._notes = notes

    @property
    def parent_case(self):
        """Return the **Parent Case** for the Task."""
        if self._parent_case:
            return self.tcex.cm.case(**self._parent_case)
        return self._parent_case

    @property
    def required(self):
        """Return the **Required** for the Task"""
        return self._required

    @property
    def status(self):
        """Return the **Status** for the Task"""
        return self._status

    @status.setter
    def status(self, status):
        """Set the **Status** for the Task"""
        self._status = status

    @property
    def workflow_phase(self):
        """Return the **Workflow Phase** for the Task"""
        return self._workflow_phase

    @workflow_phase.setter
    def workflow_phase(self, workflow_phase):
        """Set the **Workflow Phase** for the Task"""
        self._workflow_phase = workflow_phase

    @property
    def workflow_step(self):
        """Return the **Workflow Step** for the Task"""
        return self._workflow_step

    @workflow_step.setter
    def workflow_step(self, workflow_step):
        """Set the **Workflow Step** for the Task"""
        self._workflow_step = workflow_step

    @property
    def xid(self):
        """Return the **XID** for the Task"""
        return self._xid

    @xid.setter
    def xid(self, xid):
        """Set the **XID** for the Task"""
        self._xid = xid


class FilterTasks(Filter):
    """Filter Object for Workflow Event"""

    def case_id(self, operator, case_id):
        """Filter Tasks based on **caseid** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case this Task is associated with.
        """
        self._tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def case_severity(self, operator, case_severity):
        """Filter Tasks based on **caseseverity** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_severity (str): The severity of the case associated with the task.
        """
        self._tql.add_filter('caseseverity', operator, case_severity, TQL.Type.STRING)

    def completed_date(self, operator, completed_date):
        """Filter Tasks based on **completeddate** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            completed_date (str): The completion date for the task.
        """
        self._tql.add_filter('completeddate', operator, completed_date, TQL.Type.STRING)

    def config_playbook(self, operator, config_playbook):
        """Filter Tasks based on **configplaybook** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            config_playbook (str): The playbook configuration of the task.
        """
        self._tql.add_filter('configplaybook', operator, config_playbook, TQL.Type.STRING)

    def config_task(self, operator, config_task):
        """Filter Tasks based on **configtask** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            config_task (str): The configuration of the task.
        """
        self._tql.add_filter('configtask', operator, config_task, TQL.Type.STRING)

    def description(self, operator, description):
        """Filter Tasks based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of the task.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    def due_date(self, operator, due_date):
        """Filter Tasks based on **duedate** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            due_date (str): The due date for the task.
        """
        self._tql.add_filter('duedate', operator, due_date, TQL.Type.STRING)

    def has_case(self, operator, has_case):
        """Filter Tasks based on **hascase** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            has_case (int): A nested query for association to other cases.
        """
        self._tql.add_filter('hascase', operator, has_case, TQL.Type.INTEGER)

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Tasks based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the task.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name(self, operator, name):
        """Filter Tasks based on **name** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            name (str): The name of the task.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def status(self, operator, status):
        """Filter Tasks based on **status** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            status (str): The status of the task.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def target_id(self, operator, target_id):
        """Filter Tasks based on **targetid** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_id (int): The assigned user or group ID for the task.
        """
        self._tql.add_filter('targetid', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator, target_type):
        """Filter Tasks based on **targettype** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_type (str): The target type for this task (either User or Group).
        """
        self._tql.add_filter('targettype', operator, target_type, TQL.Type.STRING)

    def xid(self, operator, xid):
        """Filter Tasks based on **xid** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            xid (str): The XID of the task.
        """
        self._tql.add_filter('xid', operator, xid, TQL.Type.STRING)
