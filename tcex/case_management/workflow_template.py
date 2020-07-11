# -*- coding: utf-8 -*-
"""ThreatConnect Workflow Template"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class WorkflowTemplates(CommonCaseManagementCollection):
    """Workflow Template Class for Case Management Collection

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
            Case Object for Workflow Template. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Workflow Event objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.WORKFLOW_TEMPLATES,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
        )

    def __iter__(self):
        """Iterate on Workflow Templates"""
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        """Map a dict to a Workflow Template.

        Args:
            entity (dict): The Workflow Template data.

        Returns:
            CaseManagement.WorkflowTemplate: An Workflow Template Object
        """
        return WorkflowTemplate(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterWorkflowTemplate Object."""
        return FilterWorkflowTemplates(ApiEndpoints.WORKFLOW_TEMPLATES, self.tcex, self.tql)


class WorkflowTemplate(CommonCaseManagement):
    """WorkflowTemplate object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        active (bool, kwargs): [Read-Only] The **Active** flag for the Workflow Template.
        assignee (Assignee, kwargs): [Read-Only] The **Assignee** for the Workflow Template.
        cases (Case, kwargs): [Read-Only] The **Cases** for the Workflow Template.
        config_artifact (str, kwargs): [Read-Only] The **Config Artifact** for the Workflow
            Template.
        config_playbook (str, kwargs): [Read-Only] The **Config Playbook** for the Workflow
            Template.
        config_task (dict, kwargs): [Read-Only] The **Config Task** for the Workflow Template.
        description (str, kwargs): The **Description** for the Workflow Template.
        name (str, kwargs): [Required] The **Name** for the Workflow Template.
        target_type (str, kwargs): [Read-Only] The **Target Type** for the Workflow Template.
        version (int, kwargs): The **Version** for the Workflow Template.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties."""
        super().__init__(tcex, ApiEndpoints.WORKFLOW_TEMPLATES, kwargs)
        self._active = kwargs.get('active', None)
        self._assignee = kwargs.get('assignee', None)
        self._cases = kwargs.get('cases', None)
        self._config_artifact = kwargs.get('config_artifact', None)
        self._config_playbook = kwargs.get('config_playbook', None)
        self._config_task = kwargs.get('config_task', None)
        self._description = kwargs.get('description', None)
        self._name = kwargs.get('name', None)
        self._version = kwargs.get('version', None)

    @property
    def active(self):
        """Return the parent **Active** flag for the Workflow Template."""
        return self._active

    @property
    def assignee(self):
        """Return the parent **Assignee** flag for the Workflow Template."""
        return self._assignee

    @property
    def as_entity(self):
        """Return the entity representation of the Workflow Event."""
        return {'type': 'Workflow Template', 'value': self.name, 'id': self.id}

    @property
    def cases(self):
        """Return the parent **Cases** for the Workflow Template."""
        return self.tcex.cm.cases(initial_response=self._cases)

    @property
    def config_artifact(self):
        """Return the parent **Config Artifact** for the Workflow Template."""
        return self._config_artifact

    @property
    def config_playbook(self):
        """Return the parent **Config Playbook** for the Workflow Template."""
        return self._config_playbook

    @property
    def config_task(self):
        """Return the parent **Config Task** for the Workflow Template."""
        return self._config_task

    @property
    def description(self):
        """Return the parent **Description** for the Workflow Template."""
        return self._description

    @description.setter
    def description(self, description):
        """Set the parent **Description** for the Workflow Template."""
        self._description = description

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = WorkflowTemplate(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def name(self):
        """Return the parent **Name** for the Workflow Template."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the parent **Name** for the Workflow Template."""
        self._name = name

    @property
    def version(self):
        """Return the parent **Version** for the Workflow Template."""
        return self._version

    @version.setter
    def version(self, version):
        """Set the parent **Version** for the Workflow Template."""
        self._version = version


class FilterWorkflowTemplates(Filter):
    """Filter Object for WorkflowTemplates"""

    def active(self, operator, active):
        """Filter Workflow Templates based on **active** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            active (bool): The active status of this template.
        """
        self._tql.add_filter('active', operator, active, TQL.Type.BOOLEAN)

    def description(self, operator, description):
        """Filter Workflow Templates based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of this template.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Workflow Templates based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the template.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name(self, operator, name):
        """Filter Workflow Templates based on **name** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            name (str): The name of this template.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def target_id(self, operator, target_id):
        """Filter Workflow Templates based on **targetId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_id (int): The ID of the target of this template.
        """
        self._tql.add_filter('targetId', operator, target_id, TQL.Type.INTEGER)

    def target_type(self, operator, target_type):
        """Filter Workflow Templates based on **targetType** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            target_type (str): The target type of this template.
        """
        self._tql.add_filter('targetType', operator, target_type, TQL.Type.STRING)

    def version(self, operator, version):
        """Filter Workflow Templates based on **version** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            version (int): The version of this template.
        """
        self._tql.add_filter('version', operator, version, TQL.Type.INTEGER)
