# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL

api_endpoint = '/v3/tags'


class Tags(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None, tql_filters=None):
        super().__init__(
            tcex, api_endpoint, initial_response=initial_response, tql_filters=tql_filters
        )
        self.tql = TQL()
        self.added_tags = []

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response, added_entities=self.added_tags)

    def owner_filter(self, operator, owner):
        """
            The ID of the tag's Organization
        """
        self.tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name_filter(self, operator, owner_name):
        """
            The name of the tag's Organization
        """
        self.tql.add_filter('ownername', operator, owner_name)

    def case_id_filter(self, operator, case_id):
        """
            The ID of the case the tag is applied to
        """
        self.tql.add_filter('case_id', operator, case_id, TQL.Type.INTEGER)

    def name_filter(self, operator, name):
        """
            The name of the tag
        """
        self.tql.add_filter('name', operator, name)

    def id_filter(self, operator, id):
        """
            The ID of the tag
        """
        self.tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def case_filter(self, operator, case):
        """
            A nested query for association to other cases
        """
        self.tql.add_filter('hascase', operator, case, TQL.Type.INTEGER)

    def entity_map(self, entity):
        return Tag(self.tcex, **entity)

    def add_tag(self, tag):
        self.added_tags.append(tag)

    @property
    def as_dict(self):
        return super().as_dict(self.added_tags)


class Tag(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, kwargs)
        self._name = kwargs.get('name', None)
        self._description = kwargs.get('description', None)

    def entity_mapper(self, entity):
        """
         Maps a dict to a Tag then updates self.

         Args:
             entity (dict): The dict to map self too.
         """
        new_case = Tag(self.tcex, **entity)
        self.__dict__.update(new_case.__dict__)

    @property
    def required_properties(self):
        return ['name', 'description']

    @property
    def available_fields(self):
        return ['case', 'description']

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
