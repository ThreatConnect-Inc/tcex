# -*- coding: utf-8 -*-
"""ThreatConnect Tag"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL


class Tags(CommonCaseManagementCollection):
    """Tags Class for Case Management Collection

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Tag. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties"""
        super().__init__(
            tcex, ApiEndpoints.TAGS, initial_response=initial_response, tql_filters=tql_filters
        )

        if initial_response:
            for item in initial_response.get('data', []):
                if isinstance(item, Tag):
                    self.added_items.append(item)
                elif isinstance(item, dict):
                    self.added_items.append(Tag(tcex, **item))
                else:
                    continue

    def __iter__(self):
        """Iterate on Tag Collection"""
        return self.iterate(initial_response=self.initial_response)

    def add_tag(self, tag):
        """Add a Tag.

        Args:
            tag (Tag): The Data Object to add.
        """
        self.added_items.append(tag)

    def entity_map(self, entity):
        """Map a dict to a Tag.

        Args:
            entity (dict): The Tag data.

        Returns:
            CaseManagement.Tag: An Tag Object
        """
        return Tag(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterTag Object."""
        return FilterTag(self.tql)


class Tag(CommonCaseManagement):
    """Tag object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        case_id (int, kwargs): The Case ID for the Tag.
        cases (dict, kwargs): The Cases for the Tag.
        description (str, kwargs): The Description for the Tag.
        name (str, kwargs): The Name for the Tag.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.TAGS, kwargs)
        self._case_id = kwargs.get('case_id', [])
        # TODO: @bpurdy - this is an array of cases. how should we handle???
        self._cases = kwargs.get('cases', [])
        self._description = kwargs.get('description', None)
        self._name = kwargs.get('name', None)

    @property
    def as_entity(self):
        """Return the entity representation of the Tag."""
        return {'type': 'Tag', 'value': self.name, 'id': self.id}

    @property
    def available_fields(self):
        """Return the available fields to fetch for a Tag."""
        return ['case', 'description']

    @property
    def cases(self):
        """Return the "Cases" for the Tag."""
        return self._cases

    @property
    def case_id(self):
        """Return the "Case ID" for the Tag."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the "Case ID" for the Tag."""
        self._case_id = case_id

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = Tag(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def description(self):
        """Return the "Description" for the Tag."""
        return self._description

    @description.setter
    def description(self, description):
        """Set the "Description" for the Tag."""
        self._description = description

    @property
    def name(self):
        """Return the "Name" for the Tag."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the "Name" for the Tag."""
        self._name = name

    @property
    def required_properties(self):
        """Return a list of required fields for a Tag."""
        return ['name']


class FilterTag:
    """Filter Object for Tag

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self._tql = tql

    def case_id(self, operator, case_id):
        """Filter objects based on "case id" field.

        Args:
            operator (enum): The enum for the required operator.
            case_id (int): The filter value.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def hascase(self, operator, case):
        """Filter objects based on "case" association.

        Args:
            operator (enum): The enum for the required operator.
            case (str): The filter value.
        """
        self._tql.add_filter('hascase', operator, case, TQL.Type.INTEGER)

    def id(self, operator, id_):
        """Filter objects based on "id" field.

        Args:
            operator (enum): The enum for the required operator.
            id_ (int): The filter value.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

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

    def name(self, operator, name):
        """Filter objects based on "name" field.

        Args:
            operator (enum): The enum for the required operator.
            name (str): The filter value.
        """
        self._tql.add_filter('name', operator, name)

    def owner(self, operator, owner):
        """Filter objects based on "owner" field.

        Args:
            operator (enum): The enum for the required operator.
            owner (int): The filter value.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator, owner_name):
        """Filter objects based on "owner name" field.

        Args:
            operator (enum): The enum for the required operator.
            owner_name (str): The filter value.
        """
        self._tql.add_filter('ownername', operator, owner_name)

    def tql(self, tql):
        """Filter objects based on TQL expression.

        Args:
            tql (str): The raw TQL string expression.
        """
        self._tql.set_raw_tql(tql)