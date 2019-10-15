# -*- coding: utf-8 -*-
class CommonCaseManagement(object):
    def __init__(self, api_endpoint, **kwargs):
        kwargs = self._transform_kwargs(**kwargs)
        self.api_endpoint = api_endpoint

    def _transform_kwargs(self, **kwargs):
        for key, value in kwargs.items():
            key = self._metadata_map.get(key, key)
            transformed_value = value
            # if key in ['date_added', 'eventDate', 'firstSeen', 'publishDate']:
            #     transformed_value = self._utils.format_datetime(value,
            #                                                   date_format='%Y-%m-%dT%H:%M:%SZ')
            kwargs[key] = transformed_value
        return kwargs

    @staticmethod
    def _metadata_map():
        return {'case_id': 'caseId', 'case_xid': 'caseXid', 'date_added': 'dateAdded'}

    def get(self):
        ...
