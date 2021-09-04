"""Victim TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.case_management.filter_abc import FilterABC
from tcex.api.tc.v3.case_management.tql import TQL


class VictimFilter(FilterABC):
    """Filter Object for Victims"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.VICTIMS.value

    def asset_name(self, operator: Enum, asset_name: str) -> None:
        """Filter Asset Name based on **assetName** keyword.

        Args:
            operator: The operator enum for the filter.
            asset_name: The asset name assigned to a victim.
        """
        self._tql.add_filter('assetName', operator, asset_name, TQL.Type.STRING)

    def asset_type(self, operator: Enum, asset_type: int) -> None:
        """Filter Asset Type ID based on **assetType** keyword.

        Args:
            operator: The operator enum for the filter.
            asset_type: The asset type ID assigned to a victim.
        """
        self._tql.add_filter('assetType', operator, asset_type, TQL.Type.INTEGER)

    def asset_typename(self, operator: Enum, asset_typename: str) -> None:
        """Filter Asset Type Name based on **assetTypename** keyword.

        Args:
            operator: The operator enum for the filter.
            asset_typename: The asset type name assigned to a victim.
        """
        self._tql.add_filter('assetTypename', operator, asset_typename, TQL.Type.STRING)

    def attribute(self, operator: Enum, attribute: str) -> None:
        """Filter attribute based on **attribute** keyword.

        Args:
            operator: The operator enum for the filter.
            attribute: None.
        """
        self._tql.add_filter('attribute', operator, attribute, TQL.Type.STRING)

    def description(self, operator: Enum, description: str) -> None:
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The description of the victim.
        """
        self._tql.add_filter('description', operator, description, TQL.Type.STRING)

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

    @property
    def has_tag(self):
        """Return **FilterTags** for further filtering."""
        from tcex.api.tc.v3.tags.filter import TagFilter

        tags = FilterTags(ApiEndpoints.TAGS, self._tcex, TQL())
        self._tql.add_filter('hasTag', TQL.Operator.EQ, tags, TQL.Type.SUB_QUERY)
        return tags

    def has_victim(self, operator: Enum, has_victim: int) -> None:
        """Filter Associated Victim based on **hasVictim** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victim: A nested query for association to other victims.
        """
        self._tql.add_filter('hasVictim', operator, has_victim, TQL.Type.INTEGER)

    def has_victim_asset(self, operator: Enum, has_victim_asset: int) -> None:
        """Filter Associated Victim Asset based on **hasVictimAsset** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victim_asset: A nested query for association to other victim assets.
        """
        self._tql.add_filter('hasVictimAsset', operator, has_victim_asset, TQL.Type.INTEGER)

    def hasattribute(self, operator: Enum, hasattribute: int) -> None:
        """Filter Associated Attribute based on **hasattribute** keyword.

        Args:
            operator: The operator enum for the filter.
            hasattribute: A nested query for association to other attributes.
        """
        self._tql.add_filter('hasattribute', operator, hasattribute, TQL.Type.INTEGER)

    def hassecuritylabel(self, operator: Enum, hassecuritylabel: int) -> None:
        """Filter Associated Security Label based on **hassecuritylabel** keyword.

        Args:
            operator: The operator enum for the filter.
            hassecuritylabel: A nested query for association to other security labels.
        """
        self._tql.add_filter('hassecuritylabel', operator, hassecuritylabel, TQL.Type.INTEGER)

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the victim.
        """
        self._tql.add_filter('id', operator, id, TQL.Type.INTEGER)

    def name(self, operator: Enum, name: str) -> None:
        """Filter Name based on **name** keyword.

        Args:
            operator: The operator enum for the filter.
            name: The name of the victim.
        """
        self._tql.add_filter('name', operator, name, TQL.Type.STRING)

    def nationality(self, operator: Enum, nationality: str) -> None:
        """Filter Nationality based on **nationality** keyword.

        Args:
            operator: The operator enum for the filter.
            nationality: The nationality of the victim.
        """
        self._tql.add_filter('nationality', operator, nationality, TQL.Type.STRING)

    def organization(self, operator: Enum, organization: str) -> None:
        """Filter Organization based on **organization** keyword.

        Args:
            operator: The operator enum for the filter.
            organization: The organization of the victim.
        """
        self._tql.add_filter('organization', operator, organization, TQL.Type.STRING)

    def owner(self, operator: Enum, owner: int) -> None:
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the victim.
        """
        self._tql.add_filter('owner', operator, owner, TQL.Type.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the victim.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TQL.Type.STRING)

    def security_label(self, operator: Enum, security_label: str) -> None:
        """Filter Security Label based on **securityLabel** keyword.

        Args:
            operator: The operator enum for the filter.
            security_label: The name of a security label applied to the victim.
        """
        self._tql.add_filter('securityLabel', operator, security_label, TQL.Type.STRING)

    def sub_org(self, operator: Enum, sub_org: str) -> None:
        """Filter Sub-organization based on **subOrg** keyword.

        Args:
            operator: The operator enum for the filter.
            sub_org: The sub-organization of the victim.
        """
        self._tql.add_filter('subOrg', operator, sub_org, TQL.Type.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The name of the victim.
        """
        self._tql.add_filter('summary', operator, summary, TQL.Type.STRING)

    def tag(self, operator: Enum, tag: str) -> None:
        """Filter Tag based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to the victim.
        """
        self._tql.add_filter('tag', operator, tag, TQL.Type.STRING)

    def tag_owner(self, operator: Enum, tag_owner: int) -> None:
        """Filter Tag Owner ID based on **tagOwner** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner: The owner ID of a tag applied to the victim.
        """
        self._tql.add_filter('tagOwner', operator, tag_owner, TQL.Type.INTEGER)

    def tag_owner_name(self, operator: Enum, tag_owner_name: str) -> None:
        """Filter Tag Owner Name based on **tagOwnerName** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner_name: The owner name of a tag applied to the victim.
        """
        self._tql.add_filter('tagOwnerName', operator, tag_owner_name, TQL.Type.STRING)

    def work_location(self, operator: Enum, work_location: str) -> None:
        """Filter Work Location based on **workLocation** keyword.

        Args:
            operator: The operator enum for the filter.
            work_location: The work location of the victim.
        """
        self._tql.add_filter('workLocation', operator, work_location, TQL.Type.STRING)
