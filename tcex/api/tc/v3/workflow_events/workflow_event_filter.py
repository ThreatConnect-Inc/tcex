"""Workflow_Event TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class WorkflowEventFilter(FilterABC):
    """Filter Object for WorkflowEvents"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.WORKFLOW_EVENTS.value

    def case_id(self, operator: Enum, case_id: int):
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case this event is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TqlType.INTEGER)

    def date_added(self, operator: Enum, date_added: str):
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the event was added.
        """
        date_added = self.utils.any_to_datetime(date_added).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def deleted(self, operator: Enum, deleted: bool):
        """Filter Deleted based on **deleted** keyword.

        Args:
            operator: The operator enum for the filter.
            deleted: The deletion status of the event.
        """
        self._tql.add_filter('deleted', operator, deleted, TqlType.BOOLEAN)

    def deleted_reason(self, operator: Enum, deleted_reason: str):
        """Filter Deleted Reason based on **deletedReason** keyword.

        Args:
            operator: The operator enum for the filter.
            deleted_reason: The reason the event was deleted.
        """
        self._tql.add_filter('deletedReason', operator, deleted_reason, TqlType.STRING)

    def event_date(self, operator: Enum, event_date: str):
        """Filter Event Date based on **eventDate** keyword.

        Args:
            operator: The operator enum for the filter.
            event_date: The date the event occurred.
        """
        event_date = self.utils.any_to_datetime(event_date).strftime('%Y-%m-%dT%H:%M:%S')
        self._tql.add_filter('eventDate', operator, event_date, TqlType.STRING)

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the event.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def link(self, operator: Enum, link: str):
        """Filter Link based on **link** keyword.

        Args:
            operator: The operator enum for the filter.
            link: The item this event pertains to, in format <type>:<id>.
        """
        self._tql.add_filter('link', operator, link, TqlType.STRING)

    def summary(self, operator: Enum, summary: str):
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: Text of the event.
        """
        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def system_generated(self, operator: Enum, system_generated: bool):
        """Filter System Generated based on **systemGenerated** keyword.

        Args:
            operator: The operator enum for the filter.
            system_generated: Flag determining if this event was created automatically by the
                system.
        """
        self._tql.add_filter('systemGenerated', operator, system_generated, TqlType.BOOLEAN)

    def user_name(self, operator: Enum, user_name: str):
        """Filter User Name based on **userName** keyword.

        Args:
            operator: The operator enum for the filter.
            user_name: The username associated with the event.
        """
        self._tql.add_filter('userName', operator, user_name, TqlType.STRING)
