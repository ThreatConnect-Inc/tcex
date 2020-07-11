# -*- coding: utf-8 -*-
"""ThreatConnect Workflow Event"""
from .api_endpoints import ApiEndpoints
from .common_case_management import CommonCaseManagement
from .common_case_management_collection import CommonCaseManagementCollection
from .filter import Filter
from .tql import TQL


class WorkflowEvents(CommonCaseManagementCollection):
    """Workflow Events Class for Case Management Collection

    .. code-block:: python
        :linenos:
        :lineno-start: 1

        # Example of params input
        {
            'result_limit': 100,  # How many results are retrieved.
            'result_start': 10,  # Starting point on retrieved results.
            'fields': ['caseId', 'summary']  # Additional fields returned on the results
        }

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        initial_response (dict, optional): Initial data in
            Case Object for Artifact. Defaults to None.
        tql_filters (list, optional): List of TQL filters. Defaults to None.
        params(dict, optional): Dict of the params to be sent while
            retrieving the Workflow Event objects.
    """

    def __init__(self, tcex, initial_response=None, tql_filters=None, params=None):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            ApiEndpoints.WORKFLOW_EVENTS,
            initial_response=initial_response,
            tql_filters=tql_filters,
            params=params,
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
        return FilterWorkflowEvents(ApiEndpoints.WORKFLOW_EVENTS, self.tcex, self.tql)


class WorkflowEvent(CommonCaseManagement):
    """WorkflowEvent object for Case Management.

    Args:
        tcex (TcEx): An instantiated instance of TcEx object.
        case_id (int, kwargs): [Required (alt: caseXid)] The **Case Id** for the Workflow Event.
        case_xid (str, kwargs): [Required (alt: caseId)] The **Case Xid** for the Workflow Event.
        date_added (str, kwargs): [Read-Only] The **Date Added** for the Workflow Event.
        deleted (bool, kwargs): [Read-Only] The **Deleted** flag for the Workflow Event.
        deleted_reason (str, kwargs): the reason for deleting the event (required input for DELETE
            operation only)
        event_date (str, kwargs): the time that the Event is logged
        link (str, kwargs): [Read-Only] The **Link** for the Workflow Event.
        link_text (str, kwargs): [Read-Only] The **Link Text** for the Workflow Event.
        notes (Note, kwargs): a list of Notes corresponding to the Event
        parent_case (Case, kwargs): [Read-Only] The **Parent Case** for the Workflow Event.
        summary (str, kwargs): [Required] The **Summary** for the Workflow Event.
        system_generated (bool, kwargs): [Read-Only] The **System Generated** flag for the Workflow
            Event.
        user (User, kwargs): [Read-Only] The **User** for the Workflow Event.
    """

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties"""
        super().__init__(tcex, ApiEndpoints.WORKFLOW_EVENTS, kwargs)
        self.workflow_event_filter = [
            {
                'keyword': 'workflowEventId',
                'operator': TQL.Operator.EQ,
                'value': self.id,
                'type': TQL.Type.INTEGER,
            }
        ]
        self._case_id = kwargs.get('case_id', None) or kwargs.get('parent_case', {}).get('id', None)
        self._case_xid = kwargs.get('case_xid', None) or kwargs.get('parent_case', {}).get(
            'xid', None
        )
        self._date_added = kwargs.get('date_added', None)
        self._deleted = kwargs.get('deleted', None)
        self._deleted_reason = kwargs.get('deleted_reason', None)
        self._event_date = kwargs.get('event_date', None)
        self._link = kwargs.get('link', None)
        self._link_text = kwargs.get('link_text', None)
        self._notes = kwargs.get('notes', None)
        self._parent_case = kwargs.get('parent_case', None)
        self._summary = kwargs.get('summary', None)
        self._system_generated = kwargs.get('system_generated', None)
        self._user = kwargs.get('user', None)

    def add_note(self, **kwargs):
        """Add a note to the workflow event."""
        self.notes.add_note(self.tcex.cm.note(**kwargs))

    @property
    def as_entity(self):
        """Return the entity representation of the Workflow Event."""
        return {'type': 'Workflow Event', 'value': self.summary, 'id': self.id}

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
        return self._case_xid

    @case_xid.setter
    def case_xid(self, case_xid):
        """Set the **Case XID** for the Workflow Event."""
        self._case_xid = case_xid

    @property
    def date_added(self):
        """Return the **Date Added** for the Workflow Event."""
        return self._date_added

    @property
    def deleted(self):
        """Return the **Deleted** flag for the Workflow Event."""
        return self._deleted

    @property
    def deleted_reason(self):
        """Return the **Deleted Reason** for the Workflow Event."""
        return self._deleted_reason

    # TODO: @mj - confirm the status of this field
    # @deleted_reason.setter
    # def deleted_reason(self, deleted_reason):
    #     """Set the **Deleted Reason** for the Workflow Event."""
    #     self._deleted_reason = deleted_reason

    @property
    def event_date(self):
        """Return the **Event Date** for the Workflow Event."""
        return self._event_date

    @event_date.setter
    def event_date(self, event_date):
        """Set the **Event Date** for the Workflow Event."""
        self._event_date = event_date

    @property
    def id(self):
        """Return the **ID** for the Workflow Event."""
        return self._id

    @id.setter
    def id(self, id):  # pylint: disable=redefined-builtin
        """Set the **ID** for the Workflow Event."""
        self._id = id

    @property
    def link(self):
        """Return the **Link** for the Workflow Event."""
        return self._link

    @property
    def link_text(self):
        """Return the **Link Text** for the Workflow Event."""
        return self._link_text

    @property
    def notes(self):
        """Return the **Notes** for the Task"""
        if self._notes is None or isinstance(self._notes, dict):
            notes = self._notes or {}
            self._notes = self.tcex.cm.notes(
                initial_response=notes, tql_filters=self.workflow_event_filter
            )
        return self._notes

    @notes.setter
    def notes(self, notes):
        """Set the **Notes** for the Task"""
        if isinstance(notes, dict):
            self._notes = self.tcex.cm.notes(
                initial_response=notes, tql_filters=self.workflow_event_filter
            )
        self._notes = notes

    @property
    def parent_case(self):
        """Return the **Parent Case** for the Task."""
        if self._parent_case:
            return self.tcex.cm.case(**self._parent_case)
        return self._parent_case

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

    @property
    def user(self):
        """Return the **User** for the Workflow Event."""
        if self._user:
            return self.tcex.cm.user(**self._user)
        return self._user


class FilterWorkflowEvents(Filter):
    """Filter Object for WorkflowEvents"""

    def case_id(self, operator, case_id):
        """Filter Workflow Events based on **caseId** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            case_id (int): The ID of the case this event is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator, date_added):
        """Filter Workflow Events based on **dateAdded** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            date_added (str): The date the event was added.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    def deleted(self, operator, deleted):
        """Filter Workflow Events based on **deleted** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            deleted (bool): The deletion status of the event.
        """
        self._tql.add_filter('deleted', operator, deleted, TQL.Type.BOOLEAN)

    # TODO: @mj - confirm the status of these fields
    # Response: https://threatconnect.slack.com/archives/GS2NQL5SP/p1579282668019800
    def deleted_reason(self, operator, deleted_reason):  # pragma: no cover
        """Filter Workflow Events based on **deletedReason** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            deleted_reason (str): The reason the event was deleted.
        """
        self._tql.add_filter('deletedReason', operator, deleted_reason, TQL.Type.STRING)

    def event_date(self, operator, event_date):
        """Filter Workflow Events based on **eventDate** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            event_date (str): The date the event occurred.
        """
        self._tql.add_filter('eventDate', operator, event_date, TQL.Type.STRING)

    def id(self, operator, id):  # pylint: disable=redefined-builtin
        """Filter Workflow Events based on **id** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            id (int): The ID of the event.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def link(self, operator, link):
        """Filter objects based on "link" field.

        Args:
            operator (enum): The enum for the required operator.
            link (str): The filter value.
        """
        self._tql.add_filter('link', operator, link)

    def summary(self, operator, summary):
        """Filter Workflow Events based on **summary** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            summary (str): Text of the event.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def system_generated(self, operator, system_generated):
        """Filter Workflow Events based on **systemGenerated** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            system_generated (bool): Flag determining if this event was created automatically by
                the system.
        """
        self._tql.add_filter('systemGenerated', operator, system_generated, TQL.Type.BOOLEAN)

    def user_name(self, operator, user_name):
        """Filter Workflow Events based on **userName** keyword.

        Args:
            operator (enum): The operator enum for the filter.
            user_name (str): The username associated with the event.
        """
        self._tql.add_filter('userName', operator, user_name, TQL.Type.STRING)
