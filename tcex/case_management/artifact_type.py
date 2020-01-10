# -*- coding: utf-8 -*-
"""ThreatConnect Case Management Artifact Type"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL


class ArtifactTypes(CommonCaseManagementCollection):
    """Artifacts Type Class for Case Management Collection

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.ARTIFACT_TYPES,
            initial_response=initial_response,
            tql_filters=tql_filters,
        )

    def __iter__(self):
        """Object iterator"""
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        """Map a dict to a Artifact.

        Args:
            entity (dict): The Artifact data.

        Returns:
            CaseManagement.Artifact: An Artifact Object
        """
        return ArtifactType(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterArtifactType Object."""
        return FilterArtifactType(self.tql)


class ArtifactType(CommonCaseManagement):
    """Artifact object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.

        description (str, kwargs): The Description for the Artifact Type.
        data_type (str, kwargs): The Data Type for the Artifact Type.
        intel_type (str, kwargs): The Intel Type for the Artifact Type.
        name (str, kwargs): The Name for the Artifact Type.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.ARTIFACT_TYPES, kwargs)
        self._description = kwargs.get('description', None)
        self._data_type = kwargs.get('data_type', None)
        self._intel_type = kwargs.get('intel_type', None)
        self._name = kwargs.get('name', None)

    @property
    def as_entity(self):
        """Return the entity representation of the Artifact Type."""
        return {'type': 'Artifact Type', 'value': self.name, 'id': self.id}

    @property
    def available_fields(self):
        """Return available fields for current object."""
        return []

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = ArtifactType(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def data_type(self):
        """Return the "Date Type" for the Artifact."""
        return self._data_type

    @data_type.setter
    def data_type(self, data_type):
        """Set the "Date Type" for the Artifact."""
        self._data_type = data_type

    @property
    def description(self):
        """Return the "Description" for the Artifact."""
        return self._description

    @description.setter
    def description(self, description):
        """Set the "Description" for the Artifact."""
        self._description = description

    @property
    def intel_type(self):
        """Return the "Intel Type" for the Artifact."""
        return self._intel_type

    @intel_type.setter
    def intel_type(self, intel_type):
        """Set the "Intel Type" for the Artifact."""
        self._intel_type = intel_type

    @property
    def name(self):
        """Return the "Name" for the Artifact."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the "Name" for the Artifact."""
        self._name = name


class FilterArtifactType:
    """Filter Object for Artifact

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self._tql = tql

    def active(self, operator, active):
        """Filter objects based on "active" field.

        Args:
            operator (enum): The enum for the required operator.
            active (bool): The filter value.
        """
        self._tql.add_filter('active', operator, active, TQL.Type.BOOLEAN)

    def data_type(self, operator, data_type):
        """Filter objects based on "data type" field.

        Args:
            operator (enum): The enum for the required operator.
            data_type (str): The filter value.
        """
        self._tql.add_filter('datatype', operator, data_type)

    def description(self, operator, description):
        """Filter objects based on "description" field.

        Args:
            operator (enum): The enum for the required operator.
            description (str): The filter value.
        """
        self._tql.add_filter('description', operator, description)

    def id(self, operator, artifact_type_id):
        """Filter objects based on "id" field.

        Args:
            operator (enum): The enum for the required operator.
            artifact_type_id (int): The filter value.
        """
        self._tql.add_filter('id', operator, artifact_type_id, TQL.Type.INTEGER)

    def intel_type(self, operator, intel_type):
        """Filter objects based on "intel type" field.

        Args:
            operator (enum): The enum for the required operator.
            intel_type (str): The filter value.
        """
        self._tql.add_filter('inteltype', operator, intel_type)

    def managed(self, operator, managed):
        """Filter objects based on "managed" field.

        Args:
            operator (enum): The enum for the required operator.
            managed (bool): The filter value.
        """
        self._tql.add_filter('managed', operator, managed, TQL.Type.BOOLEAN)

    def name(self, operator, name):
        """Filter objects based on "name" field.

        Args:
            operator (enum): The enum for the required operator.
            name (str): The filter value.
        """
        self._tql.add_filter('name', operator, name)

    def tql(self, tql):
        """Filter objects based on TQL expression.

        Args:
            tql (str): The raw TQL string for the filter.
        """
        self._tql.set_raw_tql(tql)

    def ui_element(self, operator, ui_element):
        """Filter objects based on "ui element" field.

        Args:
            operator (enum): The enum for the required operator.
            ui_element (str): The filter value.
        """
        self._tql.add_filter('uielement', operator, ui_element)
