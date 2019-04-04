# -*- coding: utf-8 -*-
"""ThreatConnect TI Security Label"""


class Filters(object):
    """Filters object ot handle adding filters to TI URL calls"""

    def __init__(self, tcex):
        self._tcex = tcex
        self._filters = []

    @property
    def filters(self):
        """ Returns: list of filters"""
        return self._filters

    @filters.setter
    def filters(self, filter_key):
        """ Sets list of filters"""
        self._filters = filter_key

    def add_filter(self, filter_key, operator, value):
        """ Adds a filter given a key, operator, and value"""
        filter_key = self._metadata_map.get(filter_key, filter_key)
        self.filters.append({'filter': filter_key, 'operator': operator, 'value': value})

    def remove_filter(self, filter_key):
        """ Removes filter, given a passed in filter key"""
        self.filters.pop(filter_key)

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
        """

        Returns: filter string to be used as a param

        """
        filter_strings = []
        for filter_key in self.filters:
            filter_strings.append(
                filter_key.get('name') + filter_key.get('operator') + filter_key.get('value')
            )

        return ','.join(filter_strings)
