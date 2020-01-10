# -*- coding: utf-8 -*-
"""ThreatConnect Workflow Template"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL


class WorkflowTemplates(CommonCaseManagementCollection):
    """[summary]

    Args:
        tcex ([type]): [description]
        initial_response ([type], optional): [description]. Defaults to None.
        tql_filters ([type], optional): [description]. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties"""
        super().__init__(
            tcex,
            ApiEndpoints.WORKFLOW_TEMPLATES,
            initial_response=initial_response,
            tql_filters=tql_filters,
        )

    def __iter__(self):
        """Iterate on Workflow Templates"""
        return self.iterate(initial_response=self.initial_response)

    def organization_id_filter(self, operator, organization_id):
        """[summary]

        Args:
            operator ([type]): [description]
            organization_id ([type]): [description]
        """
        self.tql.add_filter('organizationid', operator, organization_id, TQL.Type.INTEGER)

    def assigned_user_id_filter(self, operator, assigned_user_id):
        """[summary]

        Args:
            operator ([type]): [description]
            assigned_user_id ([type]): [description]
        """
        self.tql.add_filter('assigneduserid', operator, assigned_user_id, TQL.Type.INTEGER)

    def target_id_filter(self, operator, target_id):
        """[summary]

        Args:
            operator ([type]): [description]
            target_id ([type]): [description]
        """
        self.tql.add_filter('targetid', operator, target_id, TQL.Type.INTEGER)

    def target_type_filter(self, operator, target_type):
        """[summary]

        Args:
            operator ([type]): [description]
            target_type ([type]): [description]
        """
        self.tql.add_filter('targettype', operator, target_type)

    def config_artifact_filter(self, operator, config_artifact):
        """[summary]

        Args:
            operator ([type]): [description]
            config_artifact ([type]): [description]
        """
        self.tql.add_filter('configartifact', operator, config_artifact)

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

    def config_task_filter(self, operator, config_task):
        """[summary]

        Args:
            operator ([type]): [description]
            config_task ([type]): [description]
        """
        self.tql.add_filter('configtask', operator, config_task)

    def active_filter(self, operator, active):
        """[summary]

        Args:
            operator ([type]): [description]
            active ([type]): [description]
        """
        self.tql.add_filter('active', operator, active)

    def id_filter(self, operator, id_):
        """[summary]

        Args:
            operator ([type]): [description]
            id ([type]): [description]
        """
        self.tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def config_playbook_filter(self, operator, config_playbook):
        """[summary]

        Args:
            operator ([type]): [description]
            config_playbook ([type]): [description]
        """
        self.tql.add_filter('configplaybook', operator, config_playbook)

    def version_filter(self, operator, version):
        """[summary]

        Args:
            operator ([type]): [description]
            version ([type]): [description]
        """
        self.tql.add_filter('version', operator, version)

    def entity_map(self, entity):
        """[summary]

        Args:
            entity ([type]): [description]

        Returns:
            [type]: [description]
        """
        return WorkflowTemplate(self.tcex, **entity)


class WorkflowTemplate(CommonCaseManagement):
    """[summary]

    Args:
        tcex ([type]): [description]
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties."""
        super().__init__(tcex, ApiEndpoints.WORKFLOW_TEMPLATES, kwargs)
        self._name = kwargs.get('name', None)
        self._description = kwargs.get('description', None)
        self._active = kwargs.get('active', True)
        self._version = kwargs.get('version', None)

    @property
    def required_properties(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return ['name', 'description', 'active', 'version']

    @property
    def available_fields(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return ['assignees', 'cases', 'organizations', 'user']

    # TODO: BCS fix this
    @property
    def as_entity(self):
        """Return the entity representation of the Workflow Event."""
        return {}

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = WorkflowTemplate(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def name(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._name

    @name.setter
    def name(self, name):
        """[summary]

        Args:
            name ([type]): [description]
        """
        self._name = name

    @property
    def description(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._description

    @description.setter
    def description(self, description):
        """[summary]

        Args:
            description ([type]): [description]
        """
        self._description = description

    @property
    def active(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._active

    @active.setter
    def active(self, active):
        """[summary]

        Args:
            active ([type]): [description]
        """
        self._active = active

    @property
    def version(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._version

    @version.setter
    def version(self, version):
        """[summary]

        Args:
            version ([type]): [description]
        """
        self._version = version


class FilterWorkflowTemplate:
    """Filter Object for Workflow Event

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self._tql = tql

    @property
    def keywords(self):
        """Return supported TQL keywords."""
        keywords = []
        for prop in dir(self):
            if prop.startswith('_') or prop in ['tql']:
                continue
            # remove underscore from method name to match keyword
            keywords.append(prop.replace('_', ''))

        return keywords
