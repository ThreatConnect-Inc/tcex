# -*- coding: utf-8 -*-
"""ThreatConnect Workflow Event"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .note import Note, Notes
from .tql import TQL


class WorkflowEvents(CommonCaseManagementCollection):
    """[summary]

    Args:
        tcex ([type]): [description]
        initial_response ([type], optional): [description]. Defaults to None.
        tql_filters ([type], optional): [description]. Defaults to None.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None):
        """Initialize Class properties"""
        super().__init__(
            tcex,
            ApiEndpoints.WORKFLOW_EVENTS,
            initial_response=initial_response,
            tql_filters=tql_filters,
        )

    def __iter__(self):
        """Iterate on Workflow Events."""
        return self.iterate(initial_response=self.initial_response)

    def summary_filter(self, operator, summary):
        """[summary]

        Args:
            operator ([type]): [description]
            summary ([type]): [description]
        """
        self.tql.add_filter('summary', operator, summary)

    def deleted_filter(self, operator, deleted):
        """[summary]

        Args:
            operator ([type]): [description]
            deleted ([type]): [description]
        """
        self.tql.add_filter('deleted', operator, deleted)

    def case_id_filter(self, operator, case_id):
        """[summary]

        Args:
            operator ([type]): [description]
            case_id ([type]): [description]
        """
        self.tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def link_filter(self, operator, link):
        """[summary]

        Args:
            operator ([type]): [description]
            link ([type]): [description]
        """
        self.tql.add_filter('link', operator, link)

    def deleted_reason_filter(self, operator, deleted_reason):
        """[summary]

        Args:
            operator ([type]): [description]
            deleted_reason ([type]): [description]
        """
        self.tql.add_filter('deletedreason', operator, deleted_reason)

    def system_generated_filter(self, operator, system_generated):
        """[summary]

        Args:
            operator ([type]): [description]
            system_generated ([type]): [description]
        """
        self.tql.add_filter('systemgenerated', operator, system_generated)

    def id_filter(self, operator, id_):
        """[summary]

        Args:
            operator ([type]): [description]
            id ([type]): [description]
        """
        self.tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    def link_text_filter(self, operator, link_text):
        """[summary]

        Args:
            operator ([type]): [description]
            link_text ([type]): [description]
        """
        self.tql.add_filter('link_text', operator, link_text)

    def date_added_filter(self, operator, date_added):
        """[summary]

        Args:
            operator ([type]): [description]
            date_added ([type]): [description]
        """
        self.tql.add_filter('dateadded', operator, date_added)

    def event_date_filter(self, operator, event_date):
        """[summary]

        Args:
            operator ([type]): [description]
            event_date ([type]): [description]
        """
        self.tql.add_filter('eventdate', operator, event_date)

    def username_filter(self, operator, username):
        """[summary]

        Args:
            operator ([type]): [description]
            username ([type]): [description]
        """
        self.tql.add_filter('username', operator, username)

    def entity_map(self, entity):
        """[summary]

        Args:
            entity ([type]): [description]

        Returns:
            [type]: [description]
        """
        return WorkflowEvent(self.tcex, **entity)


class WorkflowEvent(CommonCaseManagement):
    """[summary]

    Args:
        tcex ([type]): [description]
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.WORKFLOW_EVENTS, kwargs)
        self._event_date = kwargs.get('event_date', None)
        self._date_added = kwargs.get('date_added', None)
        self._summary = kwargs.get('summary', None)
        self._deleted = kwargs.get('deleted', None)
        self._system_generated = kwargs.get('system_generated', None)
        self._case_id = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get('id', None)
        self._link = kwargs.get('link', None)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}).get('data'))

    def add_note(self, **kwargs):
        """Add a note to the workflow event."""
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def as_entity(self):
        """
        Return the entity representation of the Artifact
        """
        return {'type': 'Workflow Event', 'value': self.summary, 'id': self.id}

    def entity_mapper(self, entity):
        """Map a dict to a Workflow Event then updates self.

         Args:
             entity (dict): The dict to map self too.
         """
        new_workflow_event = WorkflowEvent(self.tcex, **entity)
        self.__dict__.update(new_workflow_event.__dict__)

    @property
    def required_properties(self):
        """Return the required fields for a workflow event

        Returns:
            list of required fields for a workflow event.
        """
        return ['summary', 'case_id']

    @property
    def available_fields(self):
        """Return the available fields to fetch for the workflow event.

        Returns:
            list of available fields to fetch for the workflow event.
        """
        return ['user', 'parentCase']

    @property
    def event_date(self):
        """Return the event date for the Workflow Event."""
        return self._event_date

    @event_date.setter
    def event_date(self, event_date):
        """Set the event date for the Workflow Event."""
        self._event_date = event_date

    @property
    def case_id(self):
        """Returns the case id for the Workflow Event."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the case id for the Workflow Event."""
        self._case_id = case_id

    @property
    def date_added(self):
        """Return the date added for the Workflow Event."""
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """Set the date added for the Workflow Event."""
        self._date_added = date_added

    @property
    def summary(self):
        """Return the summary for the Workflow Event."""
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Set the summary for the Workflow Event."""
        self._summary = summary

    @property
    def deleted(self):
        """Return if the Workflow Event is deleted."""
        return self._deleted

    @deleted.setter
    def deleted(self, deleted):
        """Set if the Workflow Event is deleted."""
        self._deleted = deleted

    @property
    def system_generated(self):
        """Return if the Workflow Event is system generated."""
        return self._system_generated

    @system_generated.setter
    def system_generated(self, system_generated):
        """Set if the Workflow Event is system generated."""
        self._system_generated = system_generated

    @property
    def link(self):
        """Return the link for the Workflow Event."""
        return self._link

    @link.setter
    def link(self, link):
        """Set the link for the Workflow Event."""
        self._link = link
