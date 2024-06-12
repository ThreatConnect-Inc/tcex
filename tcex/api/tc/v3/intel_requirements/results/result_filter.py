"""TcEx Framework Module"""

# standard library
from datetime import datetime
from enum import Enum

# third-party
from arrow import Arrow

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class ResultFilter(FilterABC):
    """Filter Object for Results"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.RESULTS.value

    def archived_date(self, operator: Enum, archived_date: Arrow | datetime | int | str):
        """Filter Archived Date based on **archivedDate** keyword.

        Args:
            operator: The operator enum for the filter.
            archived_date: The date the result was archived.
        """
        archived_date = self.util.any_to_datetime(archived_date).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('archivedDate', operator, archived_date, TqlType.STRING)

    @property
    def has_intel_requirement(self):
        """Return **IntelRequirementFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.intel_requirements.intel_requirement_filter import (
            IntelRequirementFilter,
        )

        intel_requirements = IntelRequirementFilter(Tql())
        self._tql.add_filter(
            'hasIntelRequirement', TqlOperator.EQ, intel_requirements, TqlType.SUB_QUERY
        )
        return intel_requirements

    def id(self, operator: Enum, id: int | list):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the intel query result.
        """
        if isinstance(id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def intel_id(self, operator: Enum, intel_id: int | list):
        """Filter Intel ID based on **intelId** keyword.

        Args:
            operator: The operator enum for the filter.
            intel_id: The ID of the entity related to the result.
        """
        if isinstance(intel_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('intelId', operator, intel_id, TqlType.INTEGER)

    def intel_req_id(self, operator: Enum, intel_req_id: int | list):
        """Filter ID based on **intelReqId** keyword.

        Args:
            operator: The operator enum for the filter.
            intel_req_id: The ID of the intel requirement.
        """
        if isinstance(intel_req_id, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('intelReqId', operator, intel_req_id, TqlType.INTEGER)

    def intel_type(self, operator: Enum, intel_type: list | str):
        """Filter Intel Type based on **intelType** keyword.

        Args:
            operator: The operator enum for the filter.
            intel_type: The intel type of the result.
        """
        if isinstance(intel_type, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('intelType', operator, intel_type, TqlType.STRING)

    def is_archived(self, operator: Enum, is_archived: bool):
        """Filter Archived Flag based on **isArchived** keyword.

        Args:
            operator: The operator enum for the filter.
            is_archived: A true/false indicating if the result has been archived.
        """
        self._tql.add_filter('isArchived', operator, is_archived, TqlType.BOOLEAN)

    def is_associated(self, operator: Enum, is_associated: bool):
        """Filter Associated based on **isAssociated** keyword.

        Args:
            operator: The operator enum for the filter.
            is_associated: A true/false indicating if the result has been associated.
        """
        self._tql.add_filter('isAssociated', operator, is_associated, TqlType.BOOLEAN)

    def is_false_positive(self, operator: Enum, is_false_positive: bool):
        """Filter False Positive based on **isFalsePositive** keyword.

        Args:
            operator: The operator enum for the filter.
            is_false_positive: A true/false indicating if the result has been flagged as false
                positive.
        """
        self._tql.add_filter('isFalsePositive', operator, is_false_positive, TqlType.BOOLEAN)

    def is_local(self, operator: Enum, is_local: bool):
        """Filter Sourced Internally based on **isLocal** keyword.

        Args:
            operator: The operator enum for the filter.
            is_local: A true/false indicating if the result came from ThreatConnect repository.
        """
        self._tql.add_filter('isLocal', operator, is_local, TqlType.BOOLEAN)

    def last_matched_date(self, operator: Enum, last_matched_date: Arrow | datetime | int | str):
        """Filter Last Matched Date based on **lastMatchedDate** keyword.

        Args:
            operator: The operator enum for the filter.
            last_matched_date: The date the result last matched the keyword query.
        """
        last_matched_date = self.util.any_to_datetime(last_matched_date).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('lastMatchedDate', operator, last_matched_date, TqlType.STRING)

    def owner(self, operator: Enum, owner: int | list):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the result.
        """
        if isinstance(owner, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: list | str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name for the result.
        """
        if isinstance(owner_name, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def score(self, operator: Enum, score: float | list):
        """Filter Score based on **score** keyword.

        Args:
            operator: The operator enum for the filter.
            score: The weighted score in the relevancy of the result.
        """
        if isinstance(score, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('score', operator, score, TqlType.FLOAT)

    def summary(self, operator: Enum, summary: list | str):
        """Filter Name based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary of the result.
        """
        if isinstance(summary, list) and operator not in self.list_types:
            raise RuntimeError(
                'Operator must be CONTAINS, NOT_CONTAINS, IN'
                'or NOT_IN when filtering on a list of values.'
            )

        self._tql.add_filter('summary', operator, summary, TqlType.STRING)
