# -*- coding: utf-8 -*-
"""ThreatConnect Workflow Event"""
from .assignee import User
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .note import Note, Notes
from .tql import TQL


class WorkflowEvents(CommonCaseManagementCollection):
    """Workflow Events Class for Case Management Collection

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
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

    def entity_map(self, entity):
        """Map a dict to a Workflow Event.

        Args:
            entity (dict): The Workflow Event data.

        Returns:
            CaseManagement.WorkflowEvent: An Workflow Event Object
        """
        return WorkflowEvent(self.tcex, **entity)

    @property
    def filter(self):
        """Return instance of FilterWorkflowEvent Object."""
        return FilterWorkflowEvent(self.tql)


class WorkflowEvent(CommonCaseManagement):
    """Artifact object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        case_id (int, kwargs): The Case ID for the Workflow Event.
        case_xid (int, kwargs): The Case XID for the Workflow Event.
        date_added (str, kwargs): The Date Added for the Workflow Event.
        deleted (bool, kwargs): The deleted flag for the Workflow Event.
        delete_reason (bool, kwargs): The deleted reason for the Workflow Event.
        event_date (str, kwargs): The Event Date for the Workflow Event.
        link (str, kwargs): The Link for the Workflow Event.
        link_text (str, kwargs): The Link Text for the Workflow Event.
        notes (dict, kwargs): The Notes for the Workflow Event.
        summary (str, kwargs): The Summary for the Workflow Event.
        system_generated (str, kwargs): The System Generated flag for the Workflow Event.
        user (dict, kwargs): The User for the Workflow Event.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.WORKFLOW_EVENTS, kwargs)
        self._case_id = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get('id', None)
        self._case_xid = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get(
            'xid', None
        )
        self._date_added = kwargs.get('date_added', None)
        self._deleted = kwargs.get('deleted', None)
        self._deleted_reason = kwargs.get('deleted_reason', None)
        self._event_date = kwargs.get('event_date', None)
        self._link = kwargs.get('link', None)
        self._link_text = kwargs.get('link_text', None)
        self._notes = Notes(self.tcex, kwargs.get('notes', {}).get('data'))
        self._parent_case = tcex.cm.case(**kwargs.get('parent_case', {}))
        self._summary = kwargs.get('summary', None)
        self._system_generated = kwargs.get('system_generated', None)
        self._user = User(**kwargs.get('user', {}))

    def add_note(self, **kwargs):
        """Add a note to the workflow event."""
        self._notes.add_note(Note(self.tcex, **kwargs))

    @property
    def as_entity(self):
        """Return the entity representation of the Workflow Event."""
        return {'type': 'Workflow Event', 'value': self.summary, 'id': self.id}

    @property
    def available_fields(self):
        """Return the available fields to fetch for an Artifact."""
        return ['user', 'parentCase']

    def entity_mapper(self, entity):
        """Update current object with provided object properties.

        Args:
            entity (dict): An entity dict used to update the Object.
        """
        new_workflow_event = WorkflowEvent(self.tcex, **entity)
        self.__dict__.update(new_workflow_event.__dict__)

    @property
    def case_id(self):
        """Return the **Case ID** for the Workflow Event."""
        return self._case_id

    @case_id.setter
    def case_id(self, case_id):
        """Set the **Case ID** for the Workflow Event."""
        self._case_id = case_id

    @property
    def case_xid(self):
        """Return the **Case XID** for the Workflow Event."""
        return self._case_id

    @case_xid.setter
    def case_xid(self, case_xid):
        """Set the **Case XID** for the Workflow Event."""
        self._case_xid = case_xid

    @property
    def date_added(self):
        """Return the "Date Added" for the Workflow Event."""
        return self._date_added

    @date_added.setter
    def date_added(self, date_added):
        """Set the "Date Added" for the Workflow Event."""
        self._date_added = date_added

    @property
    def deleted(self):
        """Return the **Deleted** flag for the Workflow Event."""
        return self._deleted

    @deleted.setter
    def deleted(self, deleted):
        """Set the **Deleted** flag for the Workflow Event."""
        self._deleted = deleted

    @property
    def deleted_reason(self):
        """Return the **Deleted Reason** for the Workflow Event."""
        return self._deleted_reason

    @property
    def event_date(self):
        """Return the **Event Date** for the Workflow Event."""
        return self._event_date

    @event_date.setter
    def event_date(self, event_date):
        """Set the "Event Date" for the Workflow Event."""
        self._event_date = event_date

    @property
    def link(self):
        """Return the **link** for the Workflow Event."""
        return self._link

    @link.setter
    def link(self, link):
        """Set the **Link** for the Workflow Event."""
        self._link = link

    @property
    def link_text(self):
        """Return the **Link Text** for the Workflow Event."""
        return self._link_text

    @property
    def notes(self):
        """Return the **Notes** for the Workflow Event."""
        return self._notes

    @property
    def parent_case(self):
        """Return the **Parent Case** for the Workflow Event."""
        return self._parent_case

    @property
    def required_properties(self):
        """Return a list of required fields for an Artifact."""
        return ['summary', 'case_id']

    @property
    def summary(self):
        """Return the "Summary" for the Workflow Event."""
        return self._summary

    @summary.setter
    def summary(self, summary):
        """Set the "Summary" for the Workflow Event."""
        self._summary = summary

    @property
    def system_generated(self):
        """Return the **System Generated** flag for the Workflow Event."""
        return self._system_generated

    @system_generated.setter
    def system_generated(self, system_generated):
        """Set the **System Generated** flag for the Workflow Event."""
        self._system_generated = system_generated

    @property
    def user(self):
        """Return the **User** for the Workflow Event."""
        return self._user


class FilterWorkflowEvent:
    """Filter Object for Workflow Event

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, tql):
        """Initialize Class properties"""
        self._tql = tql

    def case_id(self, operator, case_id):
        """Filter objects based on "case id" field.

        Args:
            operator (enum): The enum for the required operator.
            case id (int): The filter value.
        """
        self._tql.add_filter('caseid', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator, date_added):
        """Filter objects based on "date added" field.

        Args:
            operator (enum): The enum for the required operator.
            date_added (str): The filter value.
        """
        self._tql.add_filter('dateadded', operator, date_added)

    def deleted(self, operator, deleted):
        """Filter objects based on "deleted" field.

        Args:
            operator (enum): The enum for the required operator.
            deleted (str): The filter value.
        """
        self._tql.add_filter('deleted', operator, deleted)

    def deleted_reason(self, operator, deleted_reason):
        """Filter objects based on "deleted reason" field.

        Args:
            operator (enum): The enum for the required operator.
            deleted_reason (str): The filter value.
        """
        self._tql.add_filter('deletedreason', operator, deleted_reason)

    def event_date(self, operator, event_date):
        """Filter objects based on "event date" field.

        Args:
            operator (enum): The enum for the required operator.
            event_date (str): The filter value.
        """
        self._tql.add_filter('eventdate', operator, event_date)

    def id(self, operator, id_):
        """Filter objects based on "id" field.

        Args:
            operator (enum): The enum for the required operator.
            id_ (int): The filter value.
        """
        self._tql.add_filter('id', operator, id_, TQL.Type.INTEGER)

    @property
    def keywords(self):
        """Return supported TQL keywords."""
        keywords = []
        for prop in dir(self):
            if prop.startswith('_') or prop in ['tql']:
                continue
            # remove underscore from method name to match keyword
            keywords.append(prop.replace('_', ''))

        return keywords

    def link(self, operator, link):
        """Filter objects based on "link" field.

        Args:
            operator (enum): The enum for the required operator.
            link (str): The filter value.
        """
        self._tql.add_filter('link', operator, link)

    def link_text(self, operator, link_text):
        """Filter objects based on "link text" field.

        Args:
            operator (enum): The enum for the required operator.
            link_text (str): The filter value.
        """
        self._tql.add_filter('link_text', operator, link_text)

    def summary(self, operator, summary):
        """Filter objects based on "summary" field.

        Args:
            operator (enum): The enum for the required operator.
            summary (str): The filter value.
        """
        self._tql.add_filter('summary', operator, summary)

    def system_generated(self, operator, system_generated):
        """Filter objects based on "system generated" field.

        Args:
            operator (enum): The enum for the required operator.
            system_generated (str): The filter value.
        """
        self._tql.add_filter('systemgenerated', operator, system_generated)

    def tql(self, tql):
        """Filter objects based on TQL expression.

        Args:
            tql (str): The raw TQL string expression.
        """
        self._tql.set_raw_tql(tql)

    def username(self, operator, username):
        """Filter objects based on "username" field.

        Args:
            operator (enum): The enum for the required operator.
            username (str): The filter value.
        """
        self._tql.add_filter('username', operator, username)
