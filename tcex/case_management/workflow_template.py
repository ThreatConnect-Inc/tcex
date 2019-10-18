# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection

api_endpoint = 'v3/workflowTemplates'


class WorkflowTemplates(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return WorkflowTemplate(self.tcex, **entity)


class WorkflowTemplate(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, **kwargs)
        self._name = kwargs.get('name', None)
        self._description = kwargs.get('description', None)
        self._active = kwargs.get('active', True)
        self._version = kwargs.get('version', None)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version
