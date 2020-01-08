# -*- coding: utf-8 -*-
"""ThreatConnect Tag"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL


class Tags(CommonCaseManagementCollection):
    """[summary]

    Args:
        tcex ([type]): [description]
        initial_response ([type], optional): [description]. Defaults to None.
        tql_filters ([type], optional): [description]. Defaults to None.
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
        """Iterate over all Tags"""
        return self.iterate(initial_response=self.initial_response)

    @property
    def filter(self):
        """Return instance of FilterTag Object."""
        return FilterTag(self.tql)

    def entity_map(self, entity):
        """[summary]

        Args:
            entity ([type]): [description]

        Returns:
            [type]: [description]
        """
        return Tag(self.tcex, **entity)

    def add_tag(self, tag):
        """Add a Tag"""
        self.added_items.append(tag)


class Tag(CommonCaseManagement):
    """[summary]

    Args:
        tcex ([type]): [description]
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.TAGS, kwargs)
        self._name = kwargs.get('name', None)
        self._description = kwargs.get('description', None)

    @property
    def as_entity(self):
        """
        Return the entity representation of the Artifact
        """
        return {'type': 'Tag', 'value': self.name, 'id': self.id}

    def entity_mapper(self, entity):
        """Map a dict to a Tag then updates self.

        Args:
            entity (dict): The dict to map self too.
        """
        new_case = Tag(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def required_properties(self):
        """Return required properties for tag."""
        return ['name', 'description']

    @property
    def available_fields(self):
        """Return available fields for tag."""
        return ['case', 'description']

    @property
    def name(self):
        """Return the description"""
        return self._name

    @name.setter
    def name(self, name):
        """Set the name"""
        self._name = name

    @property
    def description(self):
        """Return the description"""
        return self._description

    @description.setter
    def description(self, description):
        """Set the description"""
        self._description = description


class FilterTag:
    """Filter Object for Tag

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self._tql = tql

    def case_id(self, operator, case_id):
        """"Filter objects based on "case id" field.

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
        """"Filter objects based on "id" field.

        Args:
            operator (enum): The enum for the required operator.
            id_ (int): The filter value.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def name(self, operator, name):
        """"Filter objects based on "name" field.

        Args:
            operator (enum): The enum for the required operator.
            name (str): The filter value.
        """
        self._tql.add_filter('name', operator, name)

    def owner(self, operator, owner):
        """"Filter objects based on "owner" field.

        Args:
            operator (enum): The enum for the required operator.
            owner (int): The filter value.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator, owner_name):
        """"Filter objects based on "owner name" field.

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
