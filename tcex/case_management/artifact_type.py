# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL

api_endpoint = '/v3/artifactTypes'


class ArtifactTypes(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)
        self.tql = TQL()

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def data_type_filter(self, operator, data_type):
        """
            The data_type of the artifact
        """
        self.tql.add_filter('datatype', operator, data_type)

    def managed_filter(self, operator, managed):
        """
            The ID of the description associated with this artifact
        """
        self.tql.add_filter('managed', operator, managed)

    def intel_type_filter(self, operator, intel_type):
        """
            The ID of the comment associated with this artifact
        """
        self.tql.add_filter('inteltype', operator, intel_type)

    def id_filter(self, operator, id):
        """
            The ID of the artifact
        """
        self.tql.add_filter('id', operator, id)

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

    def active_filter(self, operator, active):
        """
            The ID of the task associated with this artifact
        """
        self.tql.add_filter('active', operator, active)

    def ui_element_filter(self, operator, ui_element):
        """
            The type name of the artifact
        """
        self.tql.add_filter('uielement', operator, ui_element)

    def entity_map(self, entity):
        return ArtifactType(self.tcex, **entity)


class ArtifactType(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, **kwargs)
        self._name = kwargs.get('managed', None)
        self._description = kwargs.get('description_xid', None)
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
