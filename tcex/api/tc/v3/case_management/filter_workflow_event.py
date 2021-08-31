"""Workflow Event Filter"""
# standard library
from enum import Enum

# first-party
from tcex.case_management.api_endpoints import ApiEndpoints
from tcex.case_management.filter_abc import FilterABC
from tcex.case_management.tql import TQL


class FilterWorkflowEvent(FilterABC):
    """Workflow Event Filter"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.WORKFLOW_EVENTS.value

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Workflow Events based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case this event is associated with.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def date_added(self, operator: Enum, date_added: str) -> None:
        """Filter Workflow Events based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the event was added.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TQL.Type.STRING)

    def deleted(self, operator: Enum, deleted: bool) -> None:
        """Filter Workflow Events based on **deleted** keyword.

        Args:
            operator: The operator enum for the filter.
            deleted: The deletion status of the event.
        """
        self._tql.add_filter('deleted', operator, deleted, TQL.Type.BOOLEAN)

    # TODO: @mj - confirm the status of these fields
    # Response: https://threatconnect.slack.com/archives/GS2NQL5SP/p1579282668019800
    def deleted_reason(self, operator: Enum, deleted_reason: str) -> None:  # pragma: no cover
        """Filter Workflow Events based on **deletedReason** keyword.

        Args:
            operator: The operator enum for the filter.
            deleted_reason: The reason the event was deleted.
        """
        self._tql.add_filter('deletedReason', operator, deleted_reason, TQL.Type.STRING)

    def event_date(self, operator: Enum, event_date: str) -> None:
        """Filter Workflow Events based on **eventDate** keyword.

        Args:
            operator: The operator enum for the filter.
            event_date: The date the event occurred.
        """
        self._tql.add_filter('eventDate', operator, event_date, TQL.Type.STRING)

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter Workflow Events based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the event.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def link(self, operator: Enum, link: str) -> None:
        """Filter objects based on "link" field.

        Args:
            operator: The enum for the required operator.
            link: The filter value.
        """
        self._tql.add_filter('link', operator, link)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Workflow Events based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: Text of the event.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def system_generated(self, operator: Enum, system_generated: bool) -> None:
        """Filter Workflow Events based on **systemGenerated** keyword.

        Args:
            operator: The operator enum for the filter.
            system_generated: Flag determining if this event was created automatically by
                the system.
        """
        self._tql.add_filter('systemGenerated', operator, system_generated, TQL.Type.BOOLEAN)

    def user_name(self, operator: Enum, user_name: str) -> None:
        """Filter Workflow Events based on **userName** keyword.

        Args:
            operator: The operator enum for the filter.
            user_name: The username associated with the event.
        """
        self._tql.add_filter('userName', operator, user_name, TQL.Type.STRING)
