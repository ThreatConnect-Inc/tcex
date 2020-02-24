# -*- coding: utf-8 -*-
"""ThreatConnect Case Management Artifact Type"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class ArtifactTypes(CommonCaseManagementCollection):
    """Artifacts Type Class for Case Management Collection

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
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent
            while retrieving the Artifact Type objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.ARTIFACT_TYPES,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
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
        """Return instance of FilterArtifactTypes Object."""
        return FilterArtifactTypes(ApiEndpoints.ARTIFACT_TYPES, self.tcex, self.tql)


class ArtifactType(CommonCaseManagement):
    """ArtifactType object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        data_type (str, kwargs): [Read-Only] The **Data Type** for the Artifact Type.
        description (str, kwargs): [Read-Only] The **Description** for the Artifact Type.
        intel_type (str, kwargs): [Read-Only] The **Intel Type** for the Artifact Type.
        name (str, kwargs): [Read-Only] The **Name** for the Artifact Type.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.ARTIFACT_TYPES, kwargs)
        self._data_type = kwargs.get('data_type', None)
        self._description = kwargs.get('description', None)
        self._intel_type = kwargs.get('intel_type', None)
        self._name = kwargs.get('name', None)

    @property
    def as_entity(self):
        """Return the entity representation of the Artifact Type."""
        return {'type': 'Artifact Type', 'value': self.name, 'id': self.id}

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = ArtifactType(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def data_type(self):
        """Return the **Date Type** for the Artifact."""
        return self._data_type

    @property
    def description(self):
        """Return the **Description** for the Artifact."""
        return self._description

    @property
    def intel_type(self):
        """Return the **Intel Type** for the Artifact."""
        return self._intel_type

    @property
    def name(self):
        """Return the **Name** for the Artifact."""
        return self._name


class FilterArtifactTypes(Filter):
    """Filter Object for ArtifactTypes"""

    def active(self, operator, active):
        """Filter Artifact Types based on **active** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            active (bool): The active status of the artifact type.
        """
        self._tql.add_filter('active', operator, active, TQL.Type.BOOLEAN)

    def data_type(self, operator, data_type):
        """Filter Artifact Types based on **dataType** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            data_type (str): The data type of the artifact type.
        """
        self._tql.add_filter('dataType', operator, data_type, TQL.Type.STRING)

    def description(self, operator, description):
        """Filter Artifact Types based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of the artifact type.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Artifact Types based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the artifact type.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def intel_type(self, operator, intel_type):
        """Filter Artifact Types based on **intelType** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            intel_type (str): The intel type of the artifact type.
        """
        self._tql.add_filter('intelType', operator, intel_type, TQL.Type.STRING)

    def managed(self, operator, managed):
        """Filter Artifact Types based on **managed** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            managed (bool): The managed status of the artifact type.
        """
        self._tql.add_filter('managed', operator, managed, TQL.Type.BOOLEAN)

    def name(self, operator, name):
        """Filter Artifact Types based on **name** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            name (str): The name of the artifact type.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)
