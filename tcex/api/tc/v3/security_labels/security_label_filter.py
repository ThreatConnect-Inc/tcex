"""Security_Label TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql_type import TqlType


class SecurityLabelFilter(FilterABC):
    """Filter Object for SecurityLabels"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.SECURITY_LABELS.value

    def color(self, operator: Enum, color: str) -> None:
        """Filter Color based on **color** keyword.

        Args:
            operator: The operator enum for the filter.
            color: The color of the security label (in hex triplet format).
        """
        self._tql.add_filter('color', operator, color, TqlType.STRING)

    def dateadded(self, operator: Enum, dateadded: str) -> None:
        """Filter Date Added based on **dateadded** keyword.

        Args:
            operator: The operator enum for the filter.
            dateadded: The date the security label was added to the system.
        """
        self._tql.add_filter('dateadded', operator, dateadded, TqlType.STRING)

    def description(self, operator: Enum, description: str) -> None:
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the security label.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def hasgroup(self, operator: Enum, hasgroup: int) -> None:
        """Filter Associated Group based on **hasgroup** keyword.

        Args:
            operator: The operator enum for the filter.
            hasgroup: A nested query for association to other groups.
        """
        self._tql.add_filter('hasgroup', operator, hasgroup, TqlType.INTEGER)

    def hasgroupattribute(self, operator: Enum, hasgroupattribute: int) -> None:
        """Filter Associated Group based on **hasgroupattribute** keyword.

        Args:
            operator: The operator enum for the filter.
            hasgroupattribute: A nested query for association to other groups.
        """
        self._tql.add_filter('hasgroupattribute', operator, hasgroupattribute, TqlType.INTEGER)

    def hasindicator(self, operator: Enum, hasindicator: int) -> None:
        """Filter Associated Indicator based on **hasindicator** keyword.

        Args:
            operator: The operator enum for the filter.
            hasindicator: A nested query for association to other indicators.
        """
        self._tql.add_filter('hasindicator', operator, hasindicator, TqlType.INTEGER)

    def hasindicatorattribute(self, operator: Enum, hasindicatorattribute: int) -> None:
        """Filter Associated Indicator based on **hasindicatorattribute** keyword.

        Args:
            operator: The operator enum for the filter.
            hasindicatorattribute: A nested query for association to other indicators.
        """
        self._tql.add_filter(
            'hasindicatorattribute', operator, hasindicatorattribute, TqlType.INTEGER
        )

    def hasvictim(self, operator: Enum, hasvictim: int) -> None:
        """Filter Associated Victim based on **hasvictim** keyword.

        Args:
            operator: The operator enum for the filter.
            hasvictim: A nested query for association to other victims.
        """
        self._tql.add_filter('hasvictim', operator, hasvictim, TqlType.INTEGER)

    def hasvictimattribute(self, operator: Enum, hasvictimattribute: int) -> None:
        """Filter Associated Victim based on **hasvictimattribute** keyword.

        Args:
            operator: The operator enum for the filter.
            hasvictimattribute: A nested query for association to other victims.
        """
        self._tql.add_filter('hasvictimattribute', operator, hasvictimattribute, TqlType.INTEGER)

    def hasworkflowattribute(self, operator: Enum, hasworkflowattribute: int) -> None:
        """Filter Associated Workflow based on **hasworkflowattribute** keyword.

        Args:
            operator: The operator enum for the filter.
            hasworkflowattribute: A nested query for association to other workflows.
        """
        self._tql.add_filter(
            'hasworkflowattribute', operator, hasworkflowattribute, TqlType.INTEGER
        )

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the security label.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the security label.
        """
        self._tql.add_filter('name', operator, name, TqlType.STRING)

    def owner(self, operator: Enum, owner: int) -> None:
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the security label.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def ownername(self, operator: Enum, ownername: str) -> None:
        """Filter Owner Name based on **ownername** keyword.

        Args:
            operator: The operator enum for the filter.
            ownername: The owner name of the security label.
        """
        self._tql.add_filter('ownername', operator, ownername, TqlType.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The name of the security label.
        """
        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def victim_id(self, operator: Enum, victim_id: int) -> None:
        """Filter Victim ID based on **victimId** keyword.

        Args:
            operator: The operator enum for the filter.
            victim_id: The ID of the victim the security label is applied to.
        """
        self._tql.add_filter('victimId', operator, victim_id, TqlType.INTEGER)
