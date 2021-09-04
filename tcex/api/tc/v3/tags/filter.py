"""Tag TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class TagFilter(FilterABC):
    """Filter Object for Tags"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.TAGS.value

    def associated_case(self, operator: Enum, associated_case: int) -> None:
        """Filter associatedCase based on **associatedCase** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_case: None.
        """
        self._tql.add_filter('associatedCase', operator, associated_case, TQL.Type.INTEGER)

    def associated_group(self, operator: Enum, associated_group: int) -> None:
        """Filter associatedGroup based on **associatedGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_group: None.
        """
        self._tql.add_filter('associatedGroup', operator, associated_group, TQL.Type.INTEGER)

    def associated_indicator(self, operator: Enum, associated_indicator: int) -> None:
        """Filter associatedIndicator based on **associatedIndicator** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_indicator: None.
        """
        self._tql.add_filter('associatedIndicator', operator, associated_indicator, TQL.Type.INTEGER)

    def associated_victim(self, operator: Enum, associated_victim: int) -> None:
        """Filter associatedVictim based on **associatedVictim** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_victim: None.
        """
        self._tql.add_filter('associatedVictim', operator, associated_victim, TQL.Type.INTEGER)

    def case_id(self, operator: Enum, case_id: int) -> None:
        """Filter Case ID based on **caseId** keyword.

        Args:
            operator: The operator enum for the filter.
            case_id: The ID of the case the tag is applied to.
        """
        self._tql.add_filter('caseId', operator, case_id, TQL.Type.INTEGER)

    def description(self, operator: Enum, description: str) -> None:
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the tag.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

    @property
    def has_case(self):
        """Return **FilterCases** for further filtering."""
        from tcex.api.tc.v3.cases.filter import CaseFilter

        cases = FilterCases(ApiEndpoints.CASES, self._tcex, TQL())
        self._tql.add_filter('hasCase', TQL.Operator.EQ, cases, TQL.Type.SUB_QUERY)
        return cases

    def has_group(self, operator: Enum, has_group: int) -> None:
        """Filter Associated Group based on **hasGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            has_group: A nested query for association to other groups.
        """
        self._tql.add_filter('hasGroup', operator, has_group, TQL.Type.INTEGER)

    def has_indicator(self, operator: Enum, has_indicator: int) -> None:
        """Filter Associated Indicator based on **hasIndicator** keyword.

        Args:
            operator: The operator enum for the filter.
            has_indicator: A nested query for association to other indicators.
        """
        self._tql.add_filter('hasIndicator', operator, has_indicator, TQL.Type.INTEGER)

    def has_victim(self, operator: Enum, has_victim: int) -> None:
        """Filter Associated Victim based on **hasVictim** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victim: A nested query for association to other victims.
        """
        self._tql.add_filter('hasVictim', operator, has_victim, TQL.Type.INTEGER)

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the tag.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def last_used(self, operator: Enum, last_used: str) -> None:
        """Filter LastUsed based on **lastUsed** keyword.

        Args:
            operator: The operator enum for the filter.
            last_used: The date this tag was last used.
        """
        self._tql.add_filter('lastUsed', operator, last_used, TQL.Type.STRING)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the tag.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def owner(self, operator: Enum, owner: int) -> None:
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the tag.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the tag.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The name of the tag.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)
