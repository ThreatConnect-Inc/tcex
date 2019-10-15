# -*- coding: utf-8 -*-
class CommonCaseManagementCollection(object):
    def __init__(self, api_endpoint):
        self._next = None
        self._previous = None
        self._api_endpoint = api_endpoint

    def iterate(self):
        return {}

    # def json(self):
    #    generator with built in API call and pagination
    # def stix2(self):
    #    json to stix2
    # def openioc(self):
    #    json to stix2
