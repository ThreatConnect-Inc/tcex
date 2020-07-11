# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Filter Module"""


class Filters:
    """Filters module for Threat Intelligence"""

    def __init__(self, tcex):
        """Initialize class properties."""
        self._tcex = tcex
        self._filters = []

    @property
    def filters(self):
        """Return filters"""
        return self._filters

    def add_filter(self, filter_key, operator, value):
        """Add a filter given a key, operator, and value"""
        filter_key = self._metadata_map.get(filter_key, filter_key)
        self.filters.append({'name': filter_key, 'operator': operator, 'value': value})

    def remove_filter(self, filter_key):
        """Remove a filter, given a passed in filter key"""
        for f in list(self._filters):
            if f.get('name') == filter_key:
                self.filters.remove(f)

    @property
    def _metadata_map(self):
        """Return metadata map for Filter objects."""
        return {
            'date_added': 'dateAdded',
            'group.date_added': 'group.dateAdded',
            'document.file_type': 'document.fileType',
            'host.dns_active': 'host.dnsActive',
            'dns_active': 'dnsActive',
            'host.whois_active': 'host.whoisActive',
            'whois_active': 'whoisActive',
            'address.contry_name': 'address.contryName',
            'contry_name': 'contryName',
            'address.contry_code': 'address.contryCode',
            'contry_code': 'contryCode',
            'indicator.date_added': 'eventDate',
            'indicator.false_positive': 'false_positive',
            'false_positive': 'falsePositive',
            'indicator.threat_assess_score': 'indicator.threatAssessScore',
            'threat_assess_score': 'threatAssessScore',
            'indicator.threat_assess_confidence': 'indicator.threatAssessConfidence',
            'threat_assess_confidence': 'threatAssessConfidence',
            'indicator.threat_assess_rating': 'indicator.threatAssessRating',
            'threat_assess_rating': 'threatAssessRating',
        }

    @property
    def filters_string(self):
        """Return a filter string to be used as a param"""
        filter_strings = []
        for filter_key in self.filters:
            filter_strings.append(
                filter_key.get('name') + filter_key.get('operator') + filter_key.get('value')
            )

        return ','.join(filter_strings)
