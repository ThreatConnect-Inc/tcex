# -*- coding: utf-8 -*-
"""ThreatConnect Note"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .tql import TQL


class Notes(CommonCaseManagementCollection):
    """ThreatConnect Notes Object

    Args:
        tcex ([type]): [description]
        initial_response ([type], optional): [description]. Defaults to None.
        tql_filters ([type], optional): [description]. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties"""
        super().__init__(
            tcex, ApiEndpoints.NOTES, initial_response=initial_response, tql_filters=tql_filters
        )
        self.added_notes = []

    def __iter__(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self.iterate(initial_response=self.initial_response)

    def owner_filter(self, operator, owner):
        """[summary]

        Args:
            operator ([type]): [description]
            owner ([type]): [description]
        """
        self.tql.add_filter('owner', operator, owner)

    def summary_filter(self, operator, summary):
        """[summary]

        Args:
            operator ([type]): [description]
            summary ([type]): [description]
        """
        self.tql.add_filter('summary', operator, summary)

    def author_filter(self, operator, author):
        """[summary]

        Args:
            operator ([type]): [description]
            author ([type]): [description]
        """
        self.tql.add_filter('author', operator, author)

    def last_modified_filter(self, operator, last_modified):
        """[summary]

        Args:
            operator ([type]): [description]
            last_modified ([type]): [description]
        """
        self.tql.add_filter('lastmodified', operator, last_modified)

    def case_id_filter(self, operator, case_id):
        """[summary]

        Args:
            operator ([type]): [description]
            case_id ([type]): [description]
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def artifact_id_filter(self, operator, artifact_id):
        """[summary]

        Args:
            operator ([type]): [description]
            artifact_id ([type]): [description]
        """
        self.tql.add_filter('artifactid', operator, artifact_id, TQL.Type.INTEGER)

    def id_filter(self, operator, id_):
        """[summary]

        Args:
            operator ([type]): [description]
            id_ ([type]): [description]
        """
        self.tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def date_added_filter(self, operator, date_added):
        """[summary]

        Args:
            operator ([type]): [description]
            date_added ([type]): [description]
        """
        self.tql.add_filter('dateadded', operator, date_added)

    def task_id_filter(self, operator, task_id):
        """[summary]

        Args:
            operator ([type]): [description]
            task_id ([type]): [description]
        """
        self.tql.add_filter('taskid', operator, task_id, TQL.Type.INTEGER)

    def entity_map(self, entity):
        """[summary]

        Args:
            entity ([type]): [description]

        Returns:
            [type]: [description]
        """
        return Note(self.tcex, **entity)

    def add_note(self, note):
        """[summary]

        Args:
            note ([type]): [description]
        """
        self.added_notes.append(note)

    @property
    def as_dict(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return super().list_as_dict(self.added_notes)


class Note(CommonCaseManagement):
    """[summary]

    Args:
        tcex ([type]): [description]
    """

    def __init__(self, tcex, **kwargs):
        """Initialize class properties."""
        super().__init__(tcex, ApiEndpoints.NOTES, kwargs)
        self._case_id = kwargs.get('case_id', None)
        self._artifact_id = kwargs.get('artifact_id', None)
        self._task_id = kwargs.get('task_id', None)
        self._text = kwargs.get('text', None)
        self._summary = kwargs.get('summary', None)
        self._user_name = kwargs.get('user_name', None)
        self._date_added = kwargs.get('date_added')
        self._last_modified = kwargs.get('last_modified', None)
        self._edited = kwargs.get('edited', None)

    @property
    def required_properties(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return ['text']

    @property
    def available_fields(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return ['artifacts', 'caseId', 'task', 'parentCase']

    def entity_mapper(self, entity):
        """Map a dict to a Note then updates self.

        Args:
            entity (dict): The dict to map self too.
        """
        new_note = Note(self.tcex, **entity)
        self.__dict__.update(new_note.__dict__)

    @property
    def case_id(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """[summary]

        Args:
            case_id ([type]): [description]
        """
        self._case_id = case_id

    @property
    def task_id(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._task_id

    @task_id.setter
    def task_id(self, task_id):
        """[summary]

        Args:
            task_id ([type]): [description]
        """
        self._task_id = task_id

    @property
    def artifact_id(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._artifact_id

    @artifact_id.setter
    def artifact_id(self, artifact_id):
        """[summary]

        Args:
            artifact_id ([type]): [description]
        """
        self._artifact_id = artifact_id

    @property
    def text(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._text

    @text.setter
    def text(self, text):
        """[summary]

        Args:
            text ([type]): [description]
        """
        self._text = text

    @property
    def summary(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._summary

    @summary.setter
    def summary(self, summary):
        """[summary]

        Args:
            summary ([type]): [description]
        """
        self._summary = summary

    @property
    def user_name(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """[summary]

        Args:
            user_name ([type]): [description]
        """
        self._user_name = user_name

    @property
    def date_added(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """[summary]

        Args:
            date_added ([type]): [description]
        """
        self._date_added = date_added

    @property
    def last_modified(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._last_modified

    @last_modified.setter
    def last_modified(self, last_modified):
        """[summary]

        Args:
            last_modified ([type]): [description]
        """
        self._last_modified = last_modified

    @property
    def edited(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._edited

    @edited.setter
    def edited(self, edited):
        """[summary]

        Args:
            edited ([type]): [description]
        """
        self._edited = edited
