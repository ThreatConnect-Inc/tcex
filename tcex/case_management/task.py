# -*- coding: utf-8 -*-
"""ThreatConnect Task"""
from .api_endpoints import ApiEndpoints
from .assignee import Assignee
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class Tasks(CommonCaseManagementCollection):
    """Tasks Class for Case Management Collection

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # Example of params input
        {
            'result_limit': 100,  # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary']  # Additional fields returned on the results
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
            task (case_management.task.Task): The Task Object to add.
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
        """Return instance of FilterTasks Object."""
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
        dependent_on_id (str, kwargs): [Read-Only] The **Dependent On ID** for the Task.
        description (str, kwargs): The **Description** for the Task.
        due_date (str, kwargs): the due date of the Task
        duration (int, kwargs): [Read-Only] The **Duration** for the Task.
        id_dependent_on (int, kwargs): [Read-Only] The **Id_Dependent On** for the Task.
        name (str, kwargs): [Required] The **Name** for the Task.
        notes (Note, kwargs): a list of Notes corresponding to the Task
        parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Task.
        required (bool, kwargs): [Read-Only] The **Required** flag for the Task.
        status (str, kwargs): The **Status** for the Task.
        workflow_phase (int, kwargs): [Read-Only] the phase of the workflow
        workflow_step (int, kwargs): [Read-Only] the step of the workflow
        xid (str, kwargs): The **Xid** for the Task.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.TASKS, kwargs)
        self.task_filter = [
            {
                'keyword': 'taskId',
                'operator': TQL.Operator.EQ,
                'value': self.id,
                'type': TQL.Type.INTEGER,
            }
        ]

        self._artifacts = kwargs.get('artifact', None)
        self._assignee = kwargs.get('assignee', None)
        self._case_id = kwargs.get('case_id', None)
        self._case_xid = kwargs.get('case_xid', None)
        self._completed_by = kwargs.get('completed_by', None)
        self._completed_date = kwargs.get('completed_date', None)
        self._config_playbook = kwargs.get('config_playbook', None)
        self._config_task = kwargs.get('config_task', None)
        self._dependent_on_id = kwargs.get('dependent_on_id', None)
        self._description = kwargs.get('description', None)
        self._due_date = kwargs.get('due_date', None)
        self._duration = kwargs.get('duration', None)
        self._name = kwargs.get('name', None)
        self._notes = kwargs.get('notes', None)
        self._parent_case = kwargs.get('parent_case', None)
        self._required = kwargs.get('required', None)
        self._status = kwargs.get('status', None)
        self._workflow_phase = kwargs.get('workflow_phase', None)
        self._workflow_step = kwargs.get('workflow_step', None)
        self._xid = kwargs.get('xid', None)

    def add_artifact(self, **kwargs):
        """Add a artifact to the task"""
        self.artifacts.add_artifact(self.tcex.cm.artifact(**kwargs))

    def add_note(self, **kwargs):
        """Add a note to the task"""
        self.notes.add_note(self.tcex.cm.note(**kwargs))

    @property
    def artifacts(self):
        """Return the **Artifacts** for the Task."""
        if self._artifacts is None or isinstance(self._artifacts, dict):
            artifacts = self._artifacts or {}
            self._artifacts = self.tcex.cm.artifacts(
                initial_response=artifacts, tql_filters=self.task_filter
            )
        return self._artifacts

    @property
    def as_entity(self):
        """Return the entity representation of the Task."""
        return {'type': 'Task', 'value': self.name, 'id': self.id}

    @property
    def assignee(self):
        """Return the **Assignee** for the Task."""
        if isinstance(self._assignee, dict):
            return self.tcex.cm.assignee(
                type=self._assignee.get('type', 'User'), **self._assignee.get('data')
            )
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
        if self._config_task is None:
            self._config_task = ConfigTasks()
        elif isinstance(self._config_task, list):
            self._config_task = ConfigTasks(config_tasks=self._config_task)
        return self._config_task

    @property
    def dependent_on_id(self):
        """Return the **Depend On ID** for the Task"""
        return self._dependent_on_id

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
        if self._notes is None or isinstance(self._notes, dict):
            notes = self._notes or {}
            self._notes = self.tcex.cm.notes(initial_response=notes, tql_filters=self.task_filter)
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the **Notes** for the Task"""
        if isinstance(notes, dict):
            self._notes = self.tcex.cm.notes(initial_response=notes, tql_filters=self.task_filter)
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

    @property
    def workflow_step(self):
        """Return the **Workflow Step** for the Task"""
        return self._workflow_step

    @property
    def xid(self):
        """Return the **XID** for the Task"""
        return self._xid

    @xid.setter
    def xid(self, xid):
        """Set the **XID** for the Task"""
        self._xid = xid


class ConfigTasks:
    """Sub class of the Cases object. Used to map the config tasks to.

    Args:
        config_tasks (list): A array of config tasks
    """

    def __init__(self, config_tasks=None):
        """Initialize Class properties."""
        if config_tasks is None:
            config_tasks = []
        self._config_tasks = []

        for config_task in config_tasks:
            if isinstance(config_task, ConfigTask):
                self._config_tasks.append(config_task)
            else:
                self._config_tasks.append(ConfigTask(**config_task))

    @property
    def config_tasks(self):
        """Return the **ConfigTasks**."""
        return self._config_tasks

    @property
    def as_dict(self):
        """Return a dict representation of the ConfigTask class."""
        data = []
        for task in self.config_tasks:
            data.append(task.as_dict)

        return data

    @property
    def body(self):
        """Return a body representation of the ConfigTask class."""
        return {}


class ConfigTask:
    """Config Task Object for Tasks"""

    def __init__(self, **kwargs):
        """Config Task object for Tasks."""
        self._transform_kwargs(kwargs)
        self._artifact_type = kwargs.get('artifact_type', None)
        self._data_type = kwargs.get('data_type', None)
        self._intel_type = kwargs.get('intel_type', None)
        self._name = kwargs.get('name', None)
        self._required = kwargs.get('required', None)
        self._ui_element = kwargs.get('ui_element', None)
        self._ui_label = kwargs.get('ui_label', None)

    @property
    def as_dict(self):
        """Return a dict representation of the Task Config class."""
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
    def artifact_type(self):
        """Return the **Artifact Type** for the Config Task"""
        return self._artifact_type

    @property
    def body(self):
        """Return a dict representation of the Task Config class."""
        return {}

    @property
    def data_type(self):
        """Return the **Data Type** for the Config Task"""
        return self._data_type

    @property
    def intel_type(self):
        """Return the **Intel Type** for the Config Task"""
        return self._intel_type

    @property
    def _metadata_map(self):
        """Return a mapping of kwargs to expected args."""
        return {
            'artifactType': 'artifact_type',
            'dataType': 'data_type',
            'intelType': 'intel_type',
            'uiElement': 'ui_element',
            'uiLabel': 'ui_label',
        }

    @property
    def name(self):
        """Return the **Name** for the Config Task"""
        return self._name

    @property
    def required(self):
        """Return the **Required** for the Config Task"""
        return self._required

    def _transform_kwargs(self, kwargs):
        """Map the provided kwargs to expected arguments."""
        for key in dict(kwargs):
            new_key = self._metadata_map.get(key, key)
            kwargs[new_key] = kwargs.pop(key)

    @property
    def ui_label(self):
        """Return the **UI Label** for the Config Task"""
        return self._ui_label

    @property
    def ui_element(self):
        """Return the **UI Element** for the Config Task"""
        return self._ui_element


class FilterTasks(Filter):
    """Filter Object for Tasks"""

    def automated(self, operator, automated):
        """Filter Tasks based on **automated** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            automated (bool): A flag indicating whether or not the task is automated.
        """
        self._tql.add_filter('automated', operator, automated, TQL.Type.BOOLEAN)

    def case_id(self, operator, case_id):
        """Filter Tasks based on **caseId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case this Task is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def case_severity(self, operator, case_severity):
        """Filter Tasks based on **caseSeverity** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_severity (str): The severity of the case associated with the task.
        """
        self._tql.add_filter('caseSeverity', operator, case_severity, TQL.Type.STRING)

    def completed_by(self, operator, completed_by):
        """Filter Tasks based on **completedBy** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            completed_by (str): The account login of the user who completed the task.
        """
        self._tql.add_filter('completedBy', operator, completed_by, TQL.Type.STRING)

    def completed_date(self, operator, completed_date):
        """Filter Tasks based on **completedDate** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            completed_date (str): The completion date for the task.
        """
        self._tql.add_filter('completedDate', operator, completed_date, TQL.Type.STRING)

    def description(self, operator, description):
        """Filter Tasks based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of the task.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    def due_date(self, operator, due_date):
        """Filter Tasks based on **dueDate** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            due_date (str): The due date for the task.
        """
        self._tql.add_filter('dueDate', operator, due_date, TQL.Type.STRING)

    # there is not way to add an **actual** artifact to a task through the API.
    @property
    def has_artifact(self):  # pragma: no cover
        """Return **FilterArtifacts** for further filtering."""
        from .artifact import FilterArtifacts

        artifacts = FilterArtifacts(ApiEndpoints.ARTIFACTS, self._tcex, TQL())
        self._tql.add_filter('hasArtifact', TQL.Operator.EQ, artifacts, TQL.Type.SUB_QUERY)
        return artifacts

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from .case import FilterCases

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    @property
    def has_note(self):
        """Return **FilterNotes** for further filtering."""
        from .note import FilterNotes

        notes = FilterNotes(ApiEndpoints.NOTES, self._tcex, TQL())
        self._tql.add_filter('hasNote', TQL.Operator.EQ, notes, TQL.Type.SUB_QUERY)
        return notes

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

    def required(self, operator, required):
        """Filter Tasks based on **required** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            required (bool): Flag indicating whether or not the task is required.
        """
        self._tql.add_filter('required', operator, required, TQL.Type.BOOLEAN)

    def status(self, operator, status):
        """Filter Tasks based on **status** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            status (str): The status of the task.
        """
        self._tql.add_filter('status', operator, status, TQL.Type.STRING)

    def target_id(self, operator, target_id):
        """Filter Tasks based on **targetId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_id (int): The assigned user or group ID for the task.
        """
        self._tql.add_filter('targetId', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator, target_type):
        """Filter Tasks based on **targetType** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_type (str): The target type for this task (either User or Group).
        """
        self._tql.add_filter('targetType', operator, target_type, TQL.Type.STRING)

    def workflow_phase(self, operator, workflow_phase):
        """Filter Tasks based on **workflowPhase** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            workflow_phase (int): The workflow phase of the task.
        """
        self._tql.add_filter('workflowPhase', operator, workflow_phase, TQL.Type.INTEGER)

    def workflow_step(self, operator, workflow_step):
        """Filter Tasks based on **workflowStep** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            workflow_step (int): The workflow step of the task.
        """
        self._tql.add_filter('workflowStep', operator, workflow_step, TQL.Type.INTEGER)

    def xid(self, operator, xid):
        """Filter Tasks based on **xid** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            xid (str): The XID of the task.
        """
        self._tql.add_filter('xid', operator, xid, TQL.Type.STRING)
