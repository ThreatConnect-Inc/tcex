# -*- coding: utf-8 -*-
"""ThreatConnect Workflow Template"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class WorkflowTemplates(CommonCaseManagementCollection):
    """Workflow Template Class for Case Management Collection

    params example: {
        'result_limit': 100, # How many results are retrieved.
        'result_start': 10,  # Starting point on retrieved results.
        'fields': ['caseId', 'summary'] # Additional fields returned on the results
    }

    Args:
        tcex ([type]): [description]
        initial_response ([type], optional): [description]. Defaults to None.
        tql_filters ([type], optional): [description]. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Workflow Template objects.
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
        assigned_group (UserGroup, kwargs): [Read-Only] The **Assigned Group** for the Workflow
            Template.
        assigned_user (User, kwargs): [Read-Only] The **Assigned User** for the Workflow Template.
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
        self._active = kwargs.get('active', True)
        self._assigned_group = kwargs.get('assigned_group', None)
        self._assigned_user = kwargs.get('assigned_user', None)
        self._assignee = kwargs.get('assignee', None)
        self._cases = kwargs.get('cases', None)
        self._config_artifact = kwargs.get('config_artifact', None)
        self._config_playbook = kwargs.get('config_playbook', None)
        self._config_task = kwargs.get('config_task', None)
        self._description = kwargs.get('description', None)
        self._name = kwargs.get('name', None)
        self._target_type = kwargs.get('target_type', None)
        self._version = kwargs.get('version', None)

    @property
    def active(self):
        """Return the parent **Active** flag for the Workflow Template."""
        return self._active

    @property
    def assigned_group(self):
        """Return the parent **Assigned Group** flag for the Workflow Template."""
        return self._assigned_group

    @property
    def assigned_user(self):
        """Return the parent **Assigned User** flag for the Workflow Template."""
        return self._assigned_user

    @property
    def assignee(self):
        """Return the parent **Assignee** flag for the Workflow Template."""
        return self._assignee

    @property
    def as_entity(self):
        """Return the entity representation of the Workflow Event."""
        # @bpurdy - what should this be ???
        return {}

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
    def target_type(self):
        """Return the parent **Target Type** for the Workflow Template."""
        return True

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

    # TODO: @mj - checking to see if this is still valid
    def assigned_group_id(self, operator, assigned_group_id):  # pragma: no cover
        """Filter Workflow Templates based on **assignedGroupId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            assigned_group_id (int): The ID of the Group assigned to this template.
        """
        self._tql.add_filter('assignedGroupId', operator, assigned_group_id, TQL.Type.INTEGER)

    # TODO: @mj - checking to see if this is still valid
    def assigned_user_id(self, operator, assigned_user_id):  # pragma: no cover
        """Filter Workflow Templates based on **assignedUserId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            assigned_user_id (int): The ID of the User assigned to this template.
        """
        self._tql.add_filter('assignedUserId', operator, assigned_user_id, TQL.Type.INTEGER)

    # TODO: @mj - checking to see if this is still valid
    def config_artifact(self, operator, config_artifact):  # pragma: no cover
        """Filter Workflow Templates based on **configArtifact** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            config_artifact (str): The artifact config information.
        """
        self._tql.add_filter('configArtifact', operator, config_artifact, TQL.Type.STRING)

    # TODO: @mj - checking to see if this is still valid
    def config_playbook(self, operator, config_playbook):  # pragma: no cover
        """Filter Workflow Templates based on **configPlaybook** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            config_playbook (str): The playbook config information.
        """
        self._tql.add_filter('configPlaybook', operator, config_playbook, TQL.Type.STRING)

    # TODO: @mj - checking to see if this is still valid
    def config_task(self, operator, config_task):  # pragma: no cover
        """Filter Workflow Templates based on **configTask** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            config_task (str): The task config information.
        """
        self._tql.add_filter('configTask', operator, config_task, TQL.Type.STRING)

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

    # TODO: @mj - checking to see if this is still valid
    def organization_id(self, operator, organization_id):  # pragma: no cover
        """Filter Workflow Templates based on **organizationId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            organization_id (int): The ID of the organization associated with this template.
        """
        self._tql.add_filter('organizationId', operator, organization_id, TQL.Type.INTEGER)

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
