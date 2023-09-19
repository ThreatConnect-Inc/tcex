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

    def active_locked(self, operator: Enum, active_locked: bool):
        """Filter Indicator Status Locked based on **activeLocked** keyword.

        Args:
            operator: The operator enum for the filter.
            active_locked: Whether or not the indicator status is locked.
        """
        self._tql.add_filter('activeLocked', operator, active_locked, TqlType.BOOLEAN)

    def address_asn(self, operator: Enum, address_asn: int):
        """Filter ASN (Address) based on **addressAsn** keyword.

        Args:
            operator: The operator enum for the filter.
            address_asn: The Autonomous System Number (ASN) of an address.
        """
        self._tql.add_filter('addressAsn', operator, address_asn, TqlType.INTEGER)

    def address_cidr(self, operator: Enum, address_cidr: str):
        """Filter CIDR (Address) based on **addressCidr** keyword.

        Args:
            operator: The operator enum for the filter.
            address_cidr: A CIDR block used to search for a range of addresses.
        """
        self._tql.add_filter('addressCidr', operator, address_cidr, TqlType.STRING)

    def address_city(self, operator: Enum, address_city: str):
        """Filter City (Address) based on **addressCity** keyword.

        Args:
            operator: The operator enum for the filter.
            address_city: The name of the city an address is registered to.
        """
        self._tql.add_filter('addressCity', operator, address_city, TqlType.STRING)

    def address_country_code(self, operator: Enum, address_country_code: str):
        """Filter Country Code (Address) based on **addressCountryCode** keyword.

        Args:
            operator: The operator enum for the filter.
            address_country_code: The registered country code for an address.
        """
        self._tql.add_filter('addressCountryCode', operator, address_country_code, TqlType.STRING)

    def address_country_name(self, operator: Enum, address_country_name: str):
        """Filter Country Name (Address) based on **addressCountryName** keyword.

        Args:
            operator: The operator enum for the filter.
            address_country_name: The name of the country an address is registered to.
        """
        self._tql.add_filter('addressCountryName', operator, address_country_name, TqlType.STRING)

    def address_ip_val(self, operator: Enum, address_ip_val: int):
        """Filter Value (Address) based on **addressIpVal** keyword.

        Args:
            operator: The operator enum for the filter.
            address_ip_val: The numeric value of an address.
        """
        self._tql.add_filter('addressIpVal', operator, address_ip_val, TqlType.INTEGER)

    def address_is_ipv6(self, operator: Enum, address_is_ipv6: bool):
        """Filter Type (Address) based on **addressIsIpv6** keyword.

        Args:
            operator: The operator enum for the filter.
            address_is_ipv6: A boolean indicating if the address is of type Ipv6.
        """
        self._tql.add_filter('addressIsIpv6', operator, address_is_ipv6, TqlType.BOOLEAN)

    def address_registering_org(self, operator: Enum, address_registering_org: str):
        """Filter Registering Org (Address) based on **addressRegisteringOrg** keyword.

        Args:
            operator: The operator enum for the filter.
            address_registering_org: The registering organization for an address.
        """
        self._tql.add_filter(
            'addressRegisteringOrg', operator, address_registering_org, TqlType.STRING
        )

    def address_state(self, operator: Enum, address_state: str):
        """Filter State (Address) based on **addressState** keyword.

        Args:
            operator: The operator enum for the filter.
            address_state: The name of the state an address is registered to.
        """
        self._tql.add_filter('addressState', operator, address_state, TqlType.STRING)

    def address_timezone(self, operator: Enum, address_timezone: str):
        """Filter Time Zone (Address) based on **addressTimezone** keyword.

        Args:
            operator: The operator enum for the filter.
            address_timezone: The time zone an address resides within.
        """
        self._tql.add_filter('addressTimezone', operator, address_timezone, TqlType.STRING)

    def associated_group(self, operator: Enum, associated_group: int):
        """Filter associatedGroup based on **associatedGroup** keyword.

        Args:
            operator: The operator enum for the filter.
            associated_group: No description provided.
        """
        self._tql.add_filter('associatedGroup', operator, associated_group, TqlType.INTEGER)

    def attribute(self, operator: Enum, attribute: str):
        """Filter attribute based on **attribute** keyword.

        Args:
            operator: The operator enum for the filter.
            attribute: No description provided.
        """
        self._tql.add_filter('attribute', operator, attribute, TqlType.STRING)

    def confidence(self, operator: Enum, confidence: int):
        """Filter Confidence Rating based on **confidence** keyword.

        Args:
            operator: The operator enum for the filter.
            confidence: The confidence in the indicator's rating.
        """
        self._tql.add_filter('confidence', operator, confidence, TqlType.INTEGER)

    def date_added(self, operator: Enum, date_added: str):
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the indicator was added to the system.
        """
        date_added = self.utils.any_to_datetime(date_added).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def description(self, operator: Enum, description: str):
        """Filter Description based on **description** keyword.

        Args:
            operator: The operator enum for the filter.
            description: The default description of the indicator.
        """
        self._tql.add_filter('description', operator, description, TqlType.STRING)

    def dt_last_updated(self, operator: Enum, dt_last_updated: str):
        """Filter DomainTools Last Updated based on **dtLastUpdated** keyword.

        Args:
            operator: The operator enum for the filter.
            dt_last_updated: The date the indicator has been looked at with DomainTools.
        """
        dt_last_updated = self.utils.any_to_datetime(dt_last_updated).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('dtLastUpdated', operator, dt_last_updated, TqlType.STRING)

    def dt_malware_score(self, operator: Enum, dt_malware_score: int):
        """Filter DomainTools Malware Score based on **dtMalwareScore** keyword.

        Args:
            operator: The operator enum for the filter.
            dt_malware_score: The malware risk score from the DomainTools enrichment data.
        """
        self._tql.add_filter('dtMalwareScore', operator, dt_malware_score, TqlType.INTEGER)

    def dt_overall_score(self, operator: Enum, dt_overall_score: int):
        """Filter DomainTools Overall Score based on **dtOverallScore** keyword.

        Args:
            operator: The operator enum for the filter.
            dt_overall_score: The overall risk score from the DomainTools enrichment data.
        """
        self._tql.add_filter('dtOverallScore', operator, dt_overall_score, TqlType.INTEGER)

    def dt_phishing_score(self, operator: Enum, dt_phishing_score: int):
        """Filter DomainTools Phishing Score based on **dtPhishingScore** keyword.

        Args:
            operator: The operator enum for the filter.
            dt_phishing_score: The phishing risk score from the DomainTools enrichment data.
        """
        self._tql.add_filter('dtPhishingScore', operator, dt_phishing_score, TqlType.INTEGER)

    def dt_spam_score(self, operator: Enum, dt_spam_score: int):
        """Filter DomainTools Spam Score based on **dtSpamScore** keyword.

        Args:
            operator: The operator enum for the filter.
            dt_spam_score: The spam risk score from the DomainTools enrichment data.
        """
        self._tql.add_filter('dtSpamScore', operator, dt_spam_score, TqlType.INTEGER)

    def dt_status(self, operator: Enum, dt_status: bool):
        """Filter DomainTools Status based on **dtStatus** keyword.

        Args:
            operator: The operator enum for the filter.
            dt_status: The domain status (active/inactive) from the DomainTools enrichment data.
        """
        self._tql.add_filter('dtStatus', operator, dt_status, TqlType.BOOLEAN)

    def external_date_added(self, operator: Enum, external_date_added: str):
        """Filter External Date Added based on **externalDateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            external_date_added: The date and time that the indicator was first created externally.
        """
        external_date_added = self.utils.any_to_datetime(external_date_added).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('externalDateAdded', operator, external_date_added, TqlType.STRING)

    def external_date_expires(self, operator: Enum, external_date_expires: str):
        """Filter External Date Expires based on **externalDateExpires** keyword.

        Args:
            operator: The operator enum for the filter.
            external_date_expires: The date and time the indicator expires externally.
        """
        external_date_expires = self.utils.any_to_datetime(external_date_expires).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('externalDateExpires', operator, external_date_expires, TqlType.STRING)

    def external_last_modified(self, operator: Enum, external_last_modified: str):
        """Filter External Last Modified based on **externalLastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            external_last_modified: The date and time the indicator was modified externally.
        """
        external_last_modified = self.utils.any_to_datetime(external_last_modified).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter(
            'externalLastModified', operator, external_last_modified, TqlType.STRING
        )

    def false_positive_count(self, operator: Enum, false_positive_count: int):
        """Filter False Positive Count based on **falsePositiveCount** keyword.

        Args:
            operator: The operator enum for the filter.
            false_positive_count: The number of times the indicator has been flagged as a false
                positive.
        """
        self._tql.add_filter('falsePositiveCount', operator, false_positive_count, TqlType.INTEGER)

    def file_size(self, operator: Enum, file_size: int):
        """Filter Size (File) based on **fileSize** keyword.

        Args:
            operator: The operator enum for the filter.
            file_size: The size of a file.
        """
        self._tql.add_filter('fileSize', operator, file_size, TqlType.INTEGER)

    def first_seen(self, operator: Enum, first_seen: str):
        """Filter First Seen based on **firstSeen** keyword.

        Args:
            operator: The operator enum for the filter.
            first_seen: The date and time that the indicator was first seen.
        """
        first_seen = self.utils.any_to_datetime(first_seen).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('firstSeen', operator, first_seen, TqlType.STRING)

    @property
    def has_artifact(self):
        """Return **ArtifactFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.artifacts.artifact_filter import ArtifactFilter

        artifacts = ArtifactFilter(Tql())
        self._tql.add_filter('hasArtifact', TqlOperator.EQ, artifacts, TqlType.SUB_QUERY)
        return artifacts

    @property
    def has_attribute(self):
        """Return **IndicatorAttributeFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.indicator_attributes.indicator_attribute_filter import (
            IndicatorAttributeFilter,
        )

        attributes = IndicatorAttributeFilter(Tql())
        self._tql.add_filter('hasAttribute', TqlOperator.EQ, attributes, TqlType.SUB_QUERY)
        return attributes

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

    def has_intel_requirement(self, operator: Enum, has_intel_requirement: int):
        """Filter Associated Intel Requirement based on **hasIntelRequirement** keyword.

        Args:
            operator: The operator enum for the filter.
            has_intel_requirement: A nested query for association to intel requirements.
        """
        self._tql.add_filter(
            'hasIntelRequirement', operator, has_intel_requirement, TqlType.INTEGER
        )

    @property
    def has_security_label(self):
        """Return **SecurityLabel** for further filtering."""
        # first-party
        from tcex.api.tc.v3.security_labels.security_label_filter import SecurityLabelFilter

        security_labels = SecurityLabelFilter(Tql())
        self._tql.add_filter('hasSecurityLabel', TqlOperator.EQ, security_labels, TqlType.SUB_QUERY)
        return security_labels

    @property
    def has_tag(self):
        """Return **TagFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.tags.tag_filter import TagFilter

        tags = TagFilter(Tql())
        self._tql.add_filter('hasTag', TqlOperator.EQ, tags, TqlType.SUB_QUERY)
        return tags

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
        # first-party
        from tcex.api.tc.v3.victim_assets.victim_asset_filter import VictimAssetFilter

        victim_assets = VictimAssetFilter(Tql())
        self._tql.add_filter('hasVictimAsset', TqlOperator.EQ, victim_assets, TqlType.SUB_QUERY)
        return victim_assets

    def host_dns_active(self, operator: Enum, host_dns_active: bool):
        """Filter DNS Active (Host) based on **hostDnsActive** keyword.

        Args:
            operator: The operator enum for the filter.
            host_dns_active: A flag that determines whether or not DNS is active.
        """
        self._tql.add_filter('hostDnsActive', operator, host_dns_active, TqlType.BOOLEAN)

    def host_whois_active(self, operator: Enum, host_whois_active: bool):
        """Filter Whois Active (Host) based on **hostWhoisActive** keyword.

        Args:
            operator: The operator enum for the filter.
            host_whois_active: A flag that determines whether or not whois is active.
        """
        self._tql.add_filter('hostWhoisActive', operator, host_whois_active, TqlType.BOOLEAN)

    def id(self, operator: Enum, id: int):  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the indicator.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def indicator_active(self, operator: Enum, indicator_active: bool):
        """Filter Indicator Status based on **indicatorActive** keyword.

        Args:
            operator: The operator enum for the filter.
            indicator_active: The status (active/inactive) of the indicator.
        """
        self._tql.add_filter('indicatorActive', operator, indicator_active, TqlType.BOOLEAN)

    def last_false_positive(self, operator: Enum, last_false_positive: str):
        """Filter False Positive Last Observed based on **lastFalsePositive** keyword.

        Args:
            operator: The operator enum for the filter.
            last_false_positive: The date the indicator has been last flagged as a false positive.
        """
        last_false_positive = self.utils.any_to_datetime(last_false_positive).strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        self._tql.add_filter('lastFalsePositive', operator, last_false_positive, TqlType.STRING)

    def last_modified(self, operator: Enum, last_modified: str):
        """Filter Last Modified based on **lastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            last_modified: The date the indicator was last modified in the system.
        """
        last_modified = self.utils.any_to_datetime(last_modified).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('lastModified', operator, last_modified, TqlType.STRING)

    def last_observed(self, operator: Enum, last_observed: str):
        """Filter Last Observed based on **lastObserved** keyword.

        Args:
            operator: The operator enum for the filter.
            last_observed: The date the indicator has been last observed.
        """
        last_observed = self.utils.any_to_datetime(last_observed).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('lastObserved', operator, last_observed, TqlType.STRING)

    def last_seen(self, operator: Enum, last_seen: str):
        """Filter Last Seen based on **lastSeen** keyword.

        Args:
            operator: The operator enum for the filter.
            last_seen: The date and time that the indicator was last seen.
        """
        last_seen = self.utils.any_to_datetime(last_seen).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('lastSeen', operator, last_seen, TqlType.STRING)

    def observation_count(self, operator: Enum, observation_count: int):
        """Filter Observation Count based on **observationCount** keyword.

        Args:
            operator: The operator enum for the filter.
            observation_count: The number of times the indicator has been observed.
        """
        self._tql.add_filter('observationCount', operator, observation_count, TqlType.INTEGER)

    def owner(self, operator: Enum, owner: int):
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The Owner ID for the indicator.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str):
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the indicator.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def rating(self, operator: Enum, rating: int):
        """Filter Threat Rating based on **rating** keyword.

        Args:
            operator: The operator enum for the filter.
            rating: The rating of the indicator.
        """
        self._tql.add_filter('rating', operator, rating, TqlType.INTEGER)

    def security_label(self, operator: Enum, security_label: str):
        """Filter Security Label based on **securityLabel** keyword.

        Args:
            operator: The operator enum for the filter.
            security_label: The name of a security label applied to the indicator.
        """
        self._tql.add_filter('securityLabel', operator, security_label, TqlType.STRING)

    def source(self, operator: Enum, source: str):
        """Filter Source based on **source** keyword.

        Args:
            operator: The operator enum for the filter.
            source: The default source of the indicator.
        """
        self._tql.add_filter('source', operator, source, TqlType.STRING)

    def summary(self, operator: Enum, summary: str):
        """Filter Summary based on **summary** keyword.

        Args:
            operator: The operator enum for the filter.
            summary: The summary of the indicator.
        """
        self._tql.add_filter('summary', operator, summary, TqlType.STRING)

    def tag(self, operator: Enum, tag: str):
        """Filter Tag based on **tag** keyword.

        Args:
            operator: The operator enum for the filter.
            tag: The name of a tag applied to the indicator.
        """
        self._tql.add_filter('tag', operator, tag, TqlType.STRING)

    def tag_owner(self, operator: Enum, tag_owner: int):
        """Filter Tag Owner ID based on **tagOwner** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner: The ID of the owner of a tag.
        """
        self._tql.add_filter('tagOwner', operator, tag_owner, TqlType.INTEGER)

    def tag_owner_name(self, operator: Enum, tag_owner_name: str):
        """Filter Tag Owner Name based on **tagOwnerName** keyword.

        Args:
            operator: The operator enum for the filter.
            tag_owner_name: The name of the owner of a tag.
        """
        self._tql.add_filter('tagOwnerName', operator, tag_owner_name, TqlType.STRING)

    def threat_assess_score(self, operator: Enum, threat_assess_score: int):
        """Filter ThreatAssess Score based on **threatAssessScore** keyword.

        Args:
            operator: The operator enum for the filter.
            threat_assess_score: The threat-assessed score of the indicator.
        """
        self._tql.add_filter('threatAssessScore', operator, threat_assess_score, TqlType.INTEGER)

    def type(self, operator: Enum, type: int):  # pylint: disable=redefined-builtin
        """Filter Type ID based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The ID of the indicator type.
        """
        self._tql.add_filter('type', operator, type, TqlType.INTEGER)

    def type_name(self, operator: Enum, type_name: str):
        """Filter Type Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the indicator type.
        """
        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)

    def value1(self, operator: Enum, value1: str):
        """Filter value1 based on **value1** keyword.

        Args:
            operator: The operator enum for the filter.
            value1: No description provided.
        """
        self._tql.add_filter('value1', operator, value1, TqlType.STRING)

    def value2(self, operator: Enum, value2: str):
        """Filter value2 based on **value2** keyword.

        Args:
            operator: The operator enum for the filter.
            value2: No description provided.
        """
        self._tql.add_filter('value2', operator, value2, TqlType.STRING)

    def value3(self, operator: Enum, value3: str):
        """Filter value3 based on **value3** keyword.

        Args:
            operator: The operator enum for the filter.
            value3: No description provided.
        """
        self._tql.add_filter('value3', operator, value3, TqlType.STRING)

    def vt_last_updated(self, operator: Enum, vt_last_updated: str):
        """Filter Virus Total Last Updated based on **vtLastUpdated** keyword.

        Args:
            operator: The operator enum for the filter.
            vt_last_updated: The date the indicator has been looked at with Virus Total.
        """
        vt_last_updated = self.utils.any_to_datetime(vt_last_updated).strftime('%Y-%m-%d %H:%M:%S')
        self._tql.add_filter('vtLastUpdated', operator, vt_last_updated, TqlType.STRING)

    def vt_malicious_count(self, operator: Enum, vt_malicious_count: int):
        """Filter Virus Total Malicious Count based on **vtMaliciousCount** keyword.

        Args:
            operator: The operator enum for the filter.
            vt_malicious_count: The number of malicious reports for an indicator from Virus Total.
        """
        self._tql.add_filter('vtMaliciousCount', operator, vt_malicious_count, TqlType.INTEGER)
