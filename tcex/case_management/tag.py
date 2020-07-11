# -*- coding: utf-8 -*-
"""ThreatConnect Tag"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class Tags(CommonCaseManagementCollection):
    """Tags Class for Case Management Collection

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
            Case Object for Tag. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Tag objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.TAGS,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
        )

        if initial_response:
            for item in initial_response.get('data', []):
                if isinstance(item, dict):
                    item = Tag(tcex, **item)
                self.added_items.append(item)

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
        """Return instance of FilterTags Object."""
        return FilterTags(ApiEndpoints.TAGS, self.tcex, self.tql)


class Tag(CommonCaseManagement):
    """Tag object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        cases (Case, kwargs): [Read-Only] The **Cases** for the Tag.
        description (str, kwargs): a brief description of the Tag
        last_used (str, kwargs): [Read-Only] The **Last Used** for the Tag.
        name (str, kwargs): [Required] The **Name** for the Tag.
        owner (str, kwargs): [Read-Only] The **Owner** for the Tag.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.TAGS, kwargs)
        self._cases = kwargs.get('cases', None)
        self._description = kwargs.get('description', None)
        self._last_used = kwargs.get('last_used', None)
        self._name = kwargs.get('name', None)
        self._owner = kwargs.get('owner', None)

    @property
    def as_entity(self):
        """Return the entity representation of the Tag."""
        return {'type': 'Tag', 'value': self.name, 'id': self.id}

    @property
    def cases(self):
        """Return the **Cases** for the Tag."""
        if self._cases:
            return self.tcex.cm.cases(initial_response=self._cases)
        return self._cases

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_case = Tag(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def description(self):
        """Return the **Description** for the Tag."""
        return self._description

    @description.setter
    def description(self, description):
        """Set the **Description** for the Tag."""
        self._description = description

    @property
    def last_used(self):
        """Return the **Last Used** for the Tag."""
        return self._last_used

    @property
    def name(self):
        """Return the **Name** for the Tag."""
        return self._name

    @name.setter
    def name(self, name):
        """Set the **Name** for the Tag."""
        self._name = name

    @property
    def owner(self):
        """Return the **Owner** for the Tag."""
        return self._owner


class FilterTags(Filter):
    """Filter Object for Tags"""

    def case_id(self, operator, case_id):
        """Filter Tags based on **caseId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case the tag is applied to.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def description(self, operator, description):
        """Filter Tags based on **description** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            description (str): The description of the tag.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from .case import FilterCases

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Tags based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the tag.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def last_used(self, operator, last_used):
        """Filter Tags based on **lastUsed** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            last_used (str): The date this tag was last used.
        """
        self._tql.add_filter('lastUsed', operator, last_used, TQL.Type.STRING)

    def name(self, operator, name):
        """Filter Tags based on **name** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            name (str): The name of the tag.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def owner(self, operator, owner):
        """Filter Tags based on **owner** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner (int): The ID of the tag's Organization.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator, owner_name):
        """Filter Tags based on **ownerName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            owner_name (str): The name of the tag's Organization.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)
