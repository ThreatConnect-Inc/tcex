# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL
from .note import Note, Notes

api_endpoint = '/v3/workflowEvents'


class WorkflowEvents(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None, tql_filters=None):
        super().__init__(
            tcex, api_endpoint, initial_response=initial_response, tql_filters=tql_filters
        )
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
        super().__init__(tcex, api_endpoint, kwargs)
        self._event_date = kwargs.get('event_date', None)
        self._date_added = kwargs.get('date_added', None)
        self._summary = kwargs.get('summary', None)
        self._deleted = kwargs.get('deleted', None)
        self._system_generated = kwargs.get('system_generated', None)
        self._case_id = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get('id', None)
        self._link = kwargs.get('link', None)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}).get('data'))

    def add_note(self, **kwargs):
        """
        Adds a note to the workflow event.
        """
        self._notes.add_note(Note(self.tcex, **kwargs))

    def entity_mapper(self, entity):
        """
         Maps a dict to a Workflow Event then updates self.

         Args:
             entity (dict): The dict to map self too.
         """
        new_workflow_event = WorkflowEvent(self.tcex, **entity)
        self.__dict__.update(new_workflow_event.__dict__)

    @property
    def required_properties(self):
        """
        The required fields for a workflow event
        Returns:
            list of required fields for a workflow event.
        """
        return ['summary', 'case_id']

    @property
    def available_fields(self):
        """
        The available fields to fetch for the workflow event.
        Returns:
            list of available fields to fetch for the workflow event.
        """
        return ['user', 'parentCase']

    @property
    def event_date(self):
        """
         Returns the event date for the Workflow Event.
         """
        return self._event_date

    @event_date.setter
    def event_date(self, event_date):
        """
        Sets the event date for the Workflow Event.
        """
        self._event_date = event_date

    @property
    def case_id(self):
        """
         Returns the case id for the Workflow Event.
         """
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """
        Sets the case id for the Workflow Event.
        """
        self._case_id = case_id

    @property
    def date_added(self):
        """
        Returns the date added for the Workflow Event.
        """
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """
        Sets the date added for the Workflow Event.
        """
        self._date_added = date_added

    @property
    def summary(self):
        """
        Returns the summary for the Workflow Event.
        """
        return self._summary

    @summary.setter
    def summary(self, summary):
        """
        Sets the summary for the Workflow Event.
        """
        self._summary = summary

    @property
    def deleted(self):
        """
        Returns if the Workflow Event is deleted.
        """
        return self._deleted

    @deleted.setter
    def deleted(self, deleted):
        """
        Sets if the Workflow Event is deleted.
        """
        self._deleted = deleted

    @property
    def system_generated(self):
        """
        Returns if the Workflow Event is system generated.
        """
        return self._system_generated

    @system_generated.setter
    def system_generated(self, system_generated):
        """
        Sets if the Workflow Event is system generated.
        """
        self._system_generated = system_generated

    @property
    def link(self):
        """
        Returns the link for the Workflow Event.
        """
        return self._link

    @link.setter
    def link(self, link):
        """
        Sets the link for the Workflow Event.
        """
        self._link = link
