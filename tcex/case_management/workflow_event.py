# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL

api_endpoint = '/v3/workflowEvents'


class WorkflowEvents(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None, tql_filters=None):
        super().__init__(tcex, api_endpoint, initial_response=initial_response,
                         tql_filters=tql_filters)
        self.tql = TQL()
        self.added_tags = []

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response, added_entities=self.added_tags)

    def summary_filter(self, operator, summary):
        """
            The summary of the artifact
        """
        self.tql.add_filter('summary', operator, summary)

    def deleted_filter(self, operator, deleted):
        """
            The summary of the artifact
        """
        self.tql.add_filter('deleted', operator, deleted)

    def case_id_filter(self, operator, case_id):
        """
            The summary of the artifact
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def link_filter(self, operator, link):
        """
            The summary of the artifact
        """
        self.tql.add_filter('link', operator, link)

    def deleted_reason_filter(self, operator, deleted_reason):
        """
            The summary of the artifact
        """
        self.tql.add_filter('deletedreason', operator, deleted_reason)

    def system_generated_filter(self, operator, system_generated):
        """
            The summary of the artifact
        """
        self.tql.add_filter('systemgenerated', operator, system_generated)

    def id_filter(self, operator, id):
        """
            The summary of the artifact
        """
        self.tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def link_text_filter(self, operator, link_text):
        """
            The summary of the artifact
        """
        self.tql.add_filter('link_text', operator, link_text)

    def date_added_filter(self, operator, date_added):
        """
            The summary of the artifact
        """
        self.tql.add_filter('dateadded', operator, date_added)

    def event_date_filter(self, operator, event_date):
        """
            The summary of the artifact
        """
        self.tql.add_filter('eventdate', operator, event_date)

    def username_filter(self, operator, username):
        """
            The summary of the artifact
        """
        self.tql.add_filter('username', operator, username)

    def entity_map(self, entity):
        return WorkflowEvent(self.tcex, **entity)

    def add_tag(self, tag):
        self.added_tags.append(tag)

    @property
    def as_dict(self):
        return super().as_dict(self.added_tags)


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
    def required_properties(self):
        return ['summary', 'case_id']

    @property
    def available_fields(self):
        return ['user', 'parentCase']

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
