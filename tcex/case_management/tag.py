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
        self.added_tags = []

        # For tags, we could be passing in a bunch of existing
        # tags (used when associating to a case) so we handle
        # appending them here
        if initial_response:
            for t in initial_response.get('data', []):
                self.added_tags.append(t)

    def __iter__(self):
        """Iterate over all Tags"""
        return self.iterate(initial_response=self.initial_response, added_entities=self.added_tags)

    def owner_filter(self, operator, owner):
        """Filter tag by owner id using the provided operator.

        Args:
            operator ([type]): [description]
            owner ([type]): [description]
        """
        self.tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name_filter(self, operator, owner_name):
        """Filter tag by owner name using provided operator.

        Args:
            operator ([type]): [description]
            owner_name ([type]): [description]
        """
        self.tql.add_filter('ownername', operator, owner_name)

    def case_id_filter(self, operator, case_id):
        """Filter tag by case id using provided operator

        Args:
            operator ([type]): [description]
            case_id ([type]): [description]
        """
        self.tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def name_filter(self, operator, name):
        """Filter tag by name using provided operator

        Args:
            operator ([type]): [description]
            name ([type]): [description]
        """
        self.tql.add_filter('name', operator, name)

    def id_filter(self, operator, id_):
        """Filter tag by ID using provided operator

        Args:
            operator ([type]): [description]
            id ([type]): [description]
        """
        self.tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def case_filter(self, operator, case):
        """Filter cases by association to other cases using provided operator

        Args:
            operator ([type]): [description]
            case ([type]): [description]
        """
        self.tql.add_filter('hascase', operator, case, TQL.Type.INTEGER)

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
        self.added_tags.append(tag)

    @property
    def as_dict(self):
        """Return Tag object as a dict"""
        return super().list_as_dict(self.added_tags)


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
