# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection

api_endpoint = '/v3/tags'


class Tags(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)
        self.added_tags = []

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response, added_entities=self.added_tags)

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
