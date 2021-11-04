"""Indicator TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class IndicatorFilter(FilterABC):
    """Filter Object for Indicators"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.INDICATORS.value

    def active_locked(self, operator: Enum, active_locked: bool) -> None:
        """Filter Indicator Status Locked based on **activeLocked** keyword.

        Args:
            operator: The operator enum for the filter.
            active_locked: Whether or not the indicator status is locked.
        """
        self._tql.add_filter('activeLocked', operator, active_locked, TqlType.BOOLEAN)

    def address_asn(self, operator: Enum, address_asn: int) -> None:
        """Filter ASN (Address) based on **addressAsn** keyword.

        Args:
            operator: The operator enum for the filter.
            address_asn: The Autonomous System Number (ASN) of an address.
        """
        self._tql.add_filter('addressAsn', operator, address_asn, TqlType.INTEGER)

    def address_cidr(self, operator: Enum, address_cidr: str) -> None:
        """Filter CIDR (Address) based on **addressCidr** keyword.

        Args:
            operator: The operator enum for the filter.
            address_cidr: A CIDR block used to search for a range of addresses.
        """
        self._tql.add_filter('addressCidr', operator, address_cidr, TqlType.STRING)

    def address_city(self, operator: Enum, address_city: str) -> None:
        """Filter City (Address) based on **addressCity** keyword.

        Args:
            operator: The operator enum for the filter.
            address_city: The name of the city an address is registered to.
        """
        self._tql.add_filter('addressCity', operator, address_city, TqlType.STRING)

    def address_countrycode(self, operator: Enum, address_countrycode: str) -> None:
        """Filter Country Code (Address) based on **addressCountrycode** keyword.

        Args:
            operator: The operator enum for the filter.
            address_countrycode: The registered country code for an address.
        """
        self._tql.add_filter('addressCountrycode', operator, address_countrycode, TqlType.STRING)

    def address_countryname(self, operator: Enum, address_countryname: str) -> None:
        """Filter Country Name (Address) based on **addressCountryname** keyword.

        Args:
            operator: The operator enum for the filter.
            address_countryname: The name of the country an address is registered to.
        """
        self._tql.add_filter('addressCountryname', operator, address_countryname, TqlType.STRING)

    def address_ipval(self, operator: Enum, address_ipval: str) -> None:
        """Filter Value (Address) based on **addressIpval** keyword.

        Args:
            operator: The operator enum for the filter.
            address_ipval: The numeric value of an address.
        """
        self._tql.add_filter('addressIpval', operator, address_ipval, TqlType.STRING)

    def address_is_ipv6(self, operator: Enum, address_is_ipv6: bool) -> None:
        """Filter Type (Address) based on **addressIsIpv6** keyword.

        Args:
            operator: The operator enum for the filter.
            address_is_ipv6: A boolean indicating if the address is of type Ipv6.
        """
        self._tql.add_filter('addressIsIpv6', operator, address_is_ipv6, TqlType.BOOLEAN)

    def address_registeringorg(self, operator: Enum, address_registeringorg: str) -> None:
        """Filter Registering Org (Address) based on **addressRegisteringorg** keyword.

        Args:
            operator: The operator enum for the filter.
            address_registeringorg: The registering organization for an address.
        """
        self._tql.add_filter(
            'addressRegisteringorg', operator, address_registeringorg, TqlType.STRING
        )

    def address_state(self, operator: Enum, address_state: str) -> None:
        """Filter State (Address) based on **addressState** keyword.

        Args:
            operator: The operator enum for the filter.
            address_state: The name of the state an address is registered to.
        """
        self._tql.add_filter('addressState', operator, address_state, TqlType.STRING)

    def address_timezone(self, operator: Enum, address_timezone: str) -> None:
        """Filter Time Zone (Address) based on **addressTimezone** keyword.

        Args:
            operator: The operator enum for the filter.
            address_timezone: The time zone an address resides within.
        """
        self._tql.add_filter('addressTimezone', operator, address_timezone, TqlType.STRING)

    def associated_group(self, operator: Enum, associated_group: int) -> None:
        """Filter associatedGroup based on **associatedGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_group: None.
        """
        self._tql.add_filter('associatedGroup', operator, associated_group, TqlType.INTEGER)

    def attribute(self, operator: Enum, attribute: str) -> None:
        """Filter attribute based on **attribute** keyword.

        Args:
            operator: The operator enum for the filter.
            attribute: None.
        """
        self._tql.add_filter('attribute', operator, attribute, TqlType.STRING)

    def confidence(self, operator: Enum, confidence: int) -> None:
        """Filter Confidence Rating based on **confidence** keyword.

        Args:
            operator: The operator enum for the filter.
            confidence: The confidence in the indicator's rating.
        """
        self._tql.add_filter('confidence', operator, confidence, TqlType.INTEGER)

    def date_added(self, operator: Enum, date_added: str) -> None:
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the indicator was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def description(self, operator: Enum, description: str) -> None:
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The default description of the indicator.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def false_positive_count(self, operator: Enum, false_positive_count: int) -> None:
        """Filter False Positive Count based on **falsePositiveCount** keyword.

        Args:
            operator: The operator enum for the filter.
            false_positive_count: The number of times the
                indicator has been flagged as a false positive.
        """
        self._tql.add_filter('falsePositiveCount', operator, false_positive_count, TqlType.INTEGER)

    def filename(self, operator: Enum, filename: str) -> None:
        """Filter Name (File) based on **filename** keyword.

        Args:
            operator: The operator enum for the filter.
            filename: The name of a file.
        """
        self._tql.add_filter('filename', operator, filename, TqlType.STRING)

    def fileoccurrence_date(self, operator: Enum, fileoccurrence_date: str) -> None:
        """Filter Occurrence Date (File) based on **fileoccurrenceDate** keyword.

        Args:
            operator: The operator enum for the filter.
            fileoccurrence_date: The occurrence date of a file.
        """
        self._tql.add_filter('fileoccurrenceDate', operator, fileoccurrence_date, TqlType.STRING)

    def filepath(self, operator: Enum, filepath: str) -> None:
        """Filter Path (File) based on **filepath** keyword.

        Args:
            operator: The operator enum for the filter.
            filepath: The path of a file.
        """
        self._tql.add_filter('filepath', operator, filepath, TqlType.STRING)

    def filesize(self, operator: Enum, filesize: str) -> None:
        """Filter Size (File) based on **filesize** keyword.

        Args:
            operator: The operator enum for the filter.
            filesize: The size of a file.
        """
        self._tql.add_filter('filesize', operator, filesize, TqlType.STRING)

    def flag1(self, operator: Enum, flag1: bool) -> None:
        """Filter flag1 based on **flag1** keyword.

        Args:
            operator: The operator enum for the filter.
            flag1: None.
        """
        self._tql.add_filter('flag1', operator, flag1, TqlType.BOOLEAN)

    def flag2(self, operator: Enum, flag2: bool) -> None:
        """Filter flag2 based on **flag2** keyword.

        Args:
            operator: The operator enum for the filter.
            flag2: None.
        """
        self._tql.add_filter('flag2', operator, flag2, TqlType.BOOLEAN)

    def flag3(self, operator: Enum, flag3: bool) -> None:
        """Filter flag3 based on **flag3** keyword.

        Args:
            operator: The operator enum for the filter.
            flag3: None.
        """
        self._tql.add_filter('flag3', operator, flag3, TqlType.BOOLEAN)

    @property
    def has_artifact(self):
        """Return **ArtifactFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter

        artifacts = ArtifactFilter(Tql())
        self._tql.add_filter('hasArtifact', TqlOperator.EQ, artifacts, TqlType.SUB_QUERY)
        return artifacts

    @property
    def has_case(self):
        """Return **CaseFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.cases.case_filter import CaseFilter

        cases = CaseFilter(Tql())
        self._tql.add_filter('hasCase', TqlOperator.EQ, cases, TqlType.SUB_QUERY)
        return cases

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
        indicators = IndicatorFilter(Tql())
        self._tql.add_filter('hasIndicator', TqlOperator.EQ, indicators, TqlType.SUB_QUERY)
        return indicators

    @property
    def has_tag(self):
        """Return **TagFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tags.tag_filter import TagFilter

        tags = TagFilter(Tql())
        self._tql.add_filter('hasTag', TqlOperator.EQ, tags, TqlType.SUB_QUERY)
        return tags

    def has_victim(self, operator: Enum, has_victim: int) -> None:
        """Filter Associated Victim based on **hasVictim** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victim: A nested query for association to other victims.
        """
        self._tql.add_filter('hasVictim', operator, has_victim, TqlType.INTEGER)

    def has_victimasset(self, operator: Enum, has_victimasset: int) -> None:
        """Filter Associated Victim Asset based on **hasVictimasset** keyword.

        Args:
            operator: The operator enum for the filter.
            has_victimasset: A nested query for association to other victim assets.
        """
        self._tql.add_filter('hasVictimasset', operator, has_victimasset, TqlType.INTEGER)

    def hasattribute(self, operator: Enum, hasattribute: int) -> None:
        """Filter Associated Attribute based on **hasattribute** keyword.

        Args:
            operator: The operator enum for the filter.
            hasattribute: A nested query for association to attributes.
        """
        self._tql.add_filter('hasattribute', operator, hasattribute, TqlType.INTEGER)

    def hassecuritylabel(self, operator: Enum, hassecuritylabel: int) -> None:
        """Filter Associated Security Label based on **hassecuritylabel** keyword.

        Args:
            operator: The operator enum for the filter.
            hassecuritylabel: A nested query for association to other security labels.
        """
        self._tql.add_filter('hassecuritylabel', operator, hassecuritylabel, TqlType.INTEGER)

    def host_dns_active(self, operator: Enum, host_dns_active: bool) -> None:
        """Filter DNS Active (Host) based on **hostDnsActive** keyword.

        Args:
            operator: The operator enum for the filter.
            host_dns_active: A flag that determines whether or not DNS is active.
        """
        self._tql.add_filter('hostDnsActive', operator, host_dns_active, TqlType.BOOLEAN)

    def host_whois_active(self, operator: Enum, host_whois_active: bool) -> None:
        """Filter Whois Active (Host) based on **hostWhoisActive** keyword.

        Args:
            operator: The operator enum for the filter.
            host_whois_active: A flag that determines whether or not whois is active.
        """
        self._tql.add_filter('hostWhoisActive', operator, host_whois_active, TqlType.BOOLEAN)

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the indicator.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def indicator_active(self, operator: Enum, indicator_active: bool) -> None:
        """Filter Indicator Status based on **indicatorActive** keyword.

        Args:
            operator: The operator enum for the filter.
            indicator_active: The status (active/inactive) of the indicator.
        """
        self._tql.add_filter('indicatorActive', operator, indicator_active, TqlType.BOOLEAN)

    def int_value1(self, operator: Enum, int_value1: str) -> None:
        """Filter intValue1 based on **intValue1** keyword.

        Args:
            operator: The operator enum for the filter.
            int_value1: None.
        """
        self._tql.add_filter('intValue1', operator, int_value1, TqlType.STRING)

    def int_value2(self, operator: Enum, int_value2: str) -> None:
        """Filter intValue2 based on **intValue2** keyword.

        Args:
            operator: The operator enum for the filter.
            int_value2: None.
        """
        self._tql.add_filter('intValue2', operator, int_value2, TqlType.STRING)

    def int_value3(self, operator: Enum, int_value3: str) -> None:
        """Filter intValue3 based on **intValue3** keyword.

        Args:
            operator: The operator enum for the filter.
            int_value3: None.
        """
        self._tql.add_filter('intValue3', operator, int_value3, TqlType.STRING)

    def last_false_positive(self, operator: Enum, last_false_positive: str) -> None:
        """Filter False Positive Last Observed based on **lastFalsePositive** keyword.

        Args:
            operator: The operator enum for the filter.
            last_false_positive: The date the indicator has been last flagged as a false positive.
        """
        self._tql.add_filter('lastFalsePositive', operator, last_false_positive, TqlType.STRING)

    def last_modified(self, operator: Enum, last_modified: str) -> None:
        """Filter Last Modified based on **lastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            last_modified: The date the indicator was last modified in the system.
        """
        self._tql.add_filter('lastModified', operator, last_modified, TqlType.STRING)

    def last_observed(self, operator: Enum, last_observed: str) -> None:
        """Filter Last Observed based on **lastObserved** keyword.

        Args:
            operator: The operator enum for the filter.
            last_observed: The date the indicator has been last observed.
        """
        self._tql.add_filter('lastObserved', operator, last_observed, TqlType.STRING)

    def observation_count(self, operator: Enum, observation_count: int) -> None:
        """Filter Observation Count based on **observationCount** keyword.

        Args:
            operator: The operator enum for the filter.
            observation_count: The number of times the indicator has been observed.
        """
        self._tql.add_filter('observationCount', operator, observation_count, TqlType.INTEGER)

    def owner(self, operator: Enum, owner: int) -> None:
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the indicator.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the indicator.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def rating(self, operator: Enum, rating: int) -> None:
        """Filter Threat Rating based on **rating** keyword.

        Args:
            operator: The operator enum for the filter.
            rating: The rating of the indicator.
        """
        self._tql.add_filter('rating', operator, rating, TqlType.INTEGER)

    def security_label(self, operator: Enum, security_label: str) -> None:
        """Filter Security Label based on **securityLabel** keyword.

        Args:
            operator: The operator enum for the filter.
            security_label: The name of a security label applied to the indicator.
        """
        self._tql.add_filter('securityLabel', operator, security_label, TqlType.STRING)

    def source(self, operator: Enum, source: str) -> None:
        """Filter Source based on **source** keyword.

        Args:
            operator: The operator enum for the filter.
            source: The default source of the indicator.
        """
        self._tql.add_filter('source', operator, source, TqlType.STRING)

    def summary(self, operator: Enum, summary: str) -> None:
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary of the indicator.
        """
        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def tag(self, operator: Enum, tag: str) -> None:
        """Filter Tag based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to the indicator.
        """
        self._tql.add_filter('tag', operator, tag, TqlType.STRING)

    def tag_owner(self, operator: Enum, tag_owner: int) -> None:
        """Filter Tag Owner ID based on **tagOwner** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner: The ID of the owner of a tag.
        """
        self._tql.add_filter('tagOwner', operator, tag_owner, TqlType.INTEGER)

    def tag_owner_name(self, operator: Enum, tag_owner_name: str) -> None:
        """Filter Tag Owner Name based on **tagOwnerName** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner_name: The name of the owner of a tag.
        """
        self._tql.add_filter('tagOwnerName', operator, tag_owner_name, TqlType.STRING)

    def threat_assess_score(self, operator: Enum, threat_assess_score: int) -> None:
        """Filter ThreatAssess Score based on **threatAssessScore** keyword.

        Args:
            operator: The operator enum for the filter.
            threat_assess_score: The threat-assessed score of the indicator.
        """
        self._tql.add_filter('threatAssessScore', operator, threat_assess_score, TqlType.INTEGER)

    def type(self, operator: Enum, type: int) -> None:  # pylint: disable=redefined-builtin
        """Filter Type ID based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The ID of the indicator type.
        """
        self._tql.add_filter('type', operator, type, TqlType.INTEGER)

    def type_name(self, operator: Enum, type_name: str) -> None:
        """Filter Type Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the indicator type.
        """
        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)

    def value1(self, operator: Enum, value1: str) -> None:
        """Filter value1 based on **value1** keyword.

        Args:
            operator: The operator enum for the filter.
            value1: None.
        """
        self._tql.add_filter('value1', operator, value1, TqlType.STRING)

    def value2(self, operator: Enum, value2: str) -> None:
        """Filter value2 based on **value2** keyword.

        Args:
            operator: The operator enum for the filter.
            value2: None.
        """
        self._tql.add_filter('value2', operator, value2, TqlType.STRING)

    def value3(self, operator: Enum, value3: str) -> None:
        """Filter value3 based on **value3** keyword.

        Args:
            operator: The operator enum for the filter.
            value3: None.
        """
        self._tql.add_filter('value3', operator, value3, TqlType.STRING)
