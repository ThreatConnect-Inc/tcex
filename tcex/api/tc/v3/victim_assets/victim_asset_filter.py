"""Victim_Asset TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class VictimAssetFilter(FilterABC):
    """Filter Object for VictimAssets"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.VICTIM_ASSETS.value

    def asset(self, operator: Enum, asset: str):
        """Filter Asset based on **asset** keyword.

        Args:
            operator: The operator enum for the filter.
            asset: The sub-type of the victim asset.
        """
        self._tql.add_filter('asset', operator, asset, TqlType.STRING)

    def associated_group(self, operator: Enum, associated_group: int):
        """Filter associatedGroup based on **associatedGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_group: No description provided.
        """
        self._tql.add_filter('associatedGroup', operator, associated_group, TqlType.INTEGER)

    @property
    def has_group(self):
        """Return **GroupFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.groups.group_filter import GroupFilter

        groups = GroupFilter(Tql())
        self._tql.add_filter('hasGroup', TqlOperator.EQ, groups, TqlType.SUB_QUERY)
        return groups

    @property
    def has_indicator(self):
        """Return **IndicatorFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter

        indicators = IndicatorFilter(Tql())
        self._tql.add_filter('hasIndicator', TqlOperator.EQ, indicators, TqlType.SUB_QUERY)
        return indicators

    @property
    def has_victim(self):
        """Return **VictimFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.victims.victim_filter import VictimFilter

        victims = VictimFilter(Tql())
        self._tql.add_filter('hasVictim', TqlOperator.EQ, victims, TqlType.SUB_QUERY)
        return victims

    @property
    def has_victim_asset(self):
        """Return **VictimAssetFilter** for further filtering."""
        victim_assets = VictimAssetFilter(Tql())
        self._tql.add_filter('hasVictimAsset', TqlOperator.EQ, victim_assets, TqlType.SUB_QUERY)
        return victim_assets

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the victim asset.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def owner(self, operator: Enum, owner: int):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the victim.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the victim.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def summary(self, operator: Enum, summary: str):
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The name of the victim asset.
        """
        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def type(self, operator: Enum, type: int):  # pylint: disable=redefined-builtin
        """Filter Type ID based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The ID of the victim asset type.
        """
        self._tql.add_filter('type', operator, type, TqlType.INTEGER)

    def type_name(self, operator: Enum, type_name: str):
        """Filter Type Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the victim asset type.
        """
        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)

    def victim_id(self, operator: Enum, victim_id: int):
        """Filter Victim ID based on **victimId** keyword.

        Args:
            operator: The operator enum for the filter.
            victim_id: The ID of the victim the victim asset is applied to.
        """
        self._tql.add_filter('victimId', operator, victim_id, TqlType.INTEGER)

    def victim_name(self, operator: Enum, victim_name: str):
        """Filter Victim Name based on **victimName** keyword.

        Args:
            operator: The operator enum for the filter.
            victim_name: The name of the victim.
        """
        self._tql.add_filter('victimName', operator, victim_name, TqlType.STRING)
