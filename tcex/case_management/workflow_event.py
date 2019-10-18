# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection

api_endpoint = 'v3/workflowEvents'


class WorkflowEvents(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return WorkflowEvent(self.tcex, **entity)


class WorkflowEvent(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, **kwargs)
        self._event_date = kwargs.get('event_date', None)
        self._date_added = kwargs.get('date_added', None)
        self._summary = kwargs.get('summary', None)
        self._deleted = kwargs.get('deleted', None)
        self._system_generated = kwargs.get('system_generated', None)
        self._link = kwargs.get('link', None)

    @property
    def event_date(self):
        return self._event_date

    @event_date.setter
    def event_date(self, event_date):
        self._event_date = event_date

    @property
    def date_added(self):
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        self._date_added = date_added

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        self._summary = summary

    @property
    def deleted(self):
        return self._deleted

    @deleted.setter
    def deleted(self, deleted):
        self._deleted = deleted

    @property
    def system_generated(self):
        return self._system_generated

    @system_generated.setter
    def system_generated(self, system_generated):
        self._system_generated = system_generated

    @property
    def link(self):
        return self._link

    @event_date.setter
    def link(self, link):
        self._link = link
