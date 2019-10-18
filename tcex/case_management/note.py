# -*- coding: utf-8 -*-
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection

api_endpoint = 'v3/notes'


class Notes(CommonCaseManagementCollection):
    def __init__(self, tcex, initial_response=None):
        super().__init__(tcex, api_endpoint, initial_response)
        self.added_notes = []

    def __iter__(self):
        return self.iterate(initial_response=self.initial_response)

    def entity_map(self, entity):
        return Note(self.tcex, **entity)

    def add_note(self, note):
        self.added_notes.append(note)

    @property
    def as_dict(self):
        return super().as_dict(self.added_notes)


class Note(CommonCaseManagement):
    def __init__(self, tcex, **kwargs):
        super().__init__(tcex, api_endpoint, kwargs)
        self._case_id = kwargs.get('case_id', None)
        self._text = kwargs.get('text', None)
        self._summary = kwargs.get('summary', None)
        self._user_name = kwargs.get('user_name', None)
        self._date_added = kwargs.get('date_added')
        self._last_modified = kwargs.get('last_modified', None)
        self._edited = kwargs.get('edited', None)

    @property
    def required_properties(self):
        return ['text']

    @property
    def available_fields(self):
        return ['artifacts', 'caseId', 'task', 'parentCase']

    @property
    def case_id(self):
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        self._case_id = case_id

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, summary):
        self._summary = summary

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        self._user_name = user_name

    @property
    def date_added(self):
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        self._date_added = date_added

    @property
    def last_modified(self):
        return self._last_modified

    @last_modified.setter
    def last_modified(self, last_modified):
        self._last_modified = last_modified

    @property
    def edited(self):
        return self._edited

    @edited.setter
    def edited(self, edited):
        self._edited = edited
