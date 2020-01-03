# -*- coding: utf-8 -*-
"""ThreatConnect Artifact Type"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL


class ArtifactTypes(CommonCaseManagementCollection):
    """ A iterable class to fetch Artifact Types"""

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """
         Initialization of the class

         Args:
             tcex:
             initial_response: Initial entity to map to.
             tql_filters: TQL filters to apply during a search.
         """
        super().__init__(
            tcex,
            ApiEndpoints.ARTIFACT_TYPES,
            initial_response=initial_response,
            tql_filters=tql_filters,
        )
        self.tql = TQL()

    def __iter__(self):
        """
        Iterates over the artifacts using the provided or applied tql filters.
        """
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
        self.tql.add_filter('managed', operator, managed, TQL.Type.BOOLEAN)

    def intel_type_filter(self, operator, intel_type):
        """
            The ID of the comment associated with this artifact
        """
        self.tql.add_filter('inteltype', operator, intel_type)

    def id_filter(self, operator, artifact_type_id):
        """
            The ID of the artifact
        """
        self.tql.add_filter('id', operator, artifact_type_id, TQL.Type.INTEGER)

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
        self.tql.add_filter('active', operator, active, TQL.Type.INTEGER)

    def ui_element_filter(self, operator, ui_element):
        """
            The type name of the artifact
        """
        self.tql.add_filter('uielement', operator, ui_element)

    def entity_map(self, entity):
        """
        Maps a dict to a Artifact Type.
        """
        return ArtifactType(self.tcex, **entity)

    @property
    def as_dict(self):
        """Returns a dict version of this object."""
        return super().list_as_dict([])


class ArtifactType(CommonCaseManagement):
    """Unique API calls for Artifact Type API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """
            Initializes the Artifacts class:
            Args:
                tcex:
                name (str): The name artifact type.
                description (str): The Case XID for the artifact type
                data_type (str): The data type for the artifact type.
                intel_type (string): The intel type for the artifact type.
        """
        super().__init__(tcex, ApiEndpoints.ARTIFACT_TYPES, kwargs)
        self._name = kwargs.get('name', None)
        self._description = kwargs.get('description', None)
        self._date_type = kwargs.get('data_type', None)
        self._intel_type = kwargs.get('intel_type', None)

    @property
    def available_fields(self):
        """Return available fields for current object."""
        return []

    def entity_mapper(self, entity):
        """
         Maps a dict to a Artifact Type then updates self.

         Args:
             entity (dict): The dict to map self too.
         """
        new_case = ArtifactType(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def name(self):
        """
        Returns the name for the Artifact Type
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name for the Artifact Type
        """
        self._name = name

    @property
    def description(self):
        """
        Returns the description for the Artifact Type
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description for the Artifact Type
        """
        self._description = description

    @property
    def data_type(self):
        """
        Returns the Data Type for the Artifact Type
        """
        return self._date_type

    @data_type.setter
    def data_type(self, data_type):
        """
        Sets the Data Type for the Artifact Type
        """
        self._date_type = data_type

    @property
    def intel_type(self):
        """
        Returns the Intel Type for the Artifact Type
        """
        return self._intel_type

    @intel_type.setter
    def intel_type(self, intel_type):
        """
        Sets the Intel Type for the Artifact Type
        """
        self._intel_type = intel_type
