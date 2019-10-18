# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection

api_endpoint = '/v3/artifactTypes'


class ArtifactTypes(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return ArtifactType(self.tcex, **entity)


class ArtifactType(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, **kwargs)
        self._name = kwargs.get('case_id', None)
        self._description = kwargs.get('case_xid', None)
        self._date_type = kwargs.get('file_data', None)
        self._intel_type = kwargs.get('intel_type', None)

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
    def data_type(self):
        return self._date_type

    @data_type.setter
    def data_type(self, data_type):
        self._date_type = data_type

    @property
    def intel_type(self):
        return self._intel_type

    @intel_type.setter
    def intel_type(self, intel_type):
        self._intel_type = intel_type
