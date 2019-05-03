# -*- coding: utf-8 -*-
"""ThreatConnect TI Group"""
from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

try:
    from urllib import quote_plus  # Python 2
except ImportError:
    from urllib.parse import quote_plus  # Python


class Group(TIMappings):
    """Unique API calls for Group API Endpoints"""

    def __init__(self, tcex, sub_type, api_entity, api_branch, name, owner=None, **kwargs):
        super(Group, self).__init__(
            tcex, 'Group', 'groups', sub_type, api_entity, api_branch, owner
        )
        if name:
            self.name = name

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @staticmethod
    def is_group():
        """

        Returns:

        """
        return True

    @property
    def _metadata_map(self):
        """Return metadata map for Group objects."""
        return {
            'date_added': 'dateAdded',
            'event_date': 'eventDate',
            'file_name': 'fileName',
            'file_text': 'fileText',
            'file_type': 'fileType',
            'first_seen': 'firstSeen',
            'from_addr': 'from',
            'publish_date': 'publishDate',
            'to_addr': 'to',
        }

    def can_create(self):
        if not self.data.get('name', None):
            return False
        return True

    def add_key_value(self, key, value):
        """
        Converts the value and adds it as a data field.

        Args:
            key:
            value:
        """
        key = self._metadata_map.get(key, key)
        if key in ['dateAdded', 'eventDate', 'firstSeen', 'publishDate']:
            self._data[key] = self._utils.format_datetime(value, date_format='%Y-%m-%dT%H:%M:%SZ')
        elif key == 'file_content':
            # file content arg is not part of Group JSON
            pass
        elif key == 'confidence':
            self._data[key] = int(value)
        elif key == 'rating':
            self._data[key] = float(value)
        elif key == 'unique_id':
            self._unique_id = quote_plus(str(value))
        else:
            self._data[key] = value

    @property
    def name(self):
        """Return Group name."""
        return self._data.get('name')

    @name.setter
    def name(self, name):
        self._data['name'] = name

    def _set_unique_id(self, json_response):
        self.unique_id = json_response.get('id', '')

    @staticmethod
    def sub_types():
        """All supported ThreatConnect Group types."""
        return {
            'Adversary': {'apiBranch': 'adversaries', 'apiEntity': 'adversary'},
            'Campaign': {'apiBranch': 'campaigns', 'apiEntity': 'campaign'},
            'Document': {'apiBranch': 'documents', 'apiEntity': 'document'},
            'Emails': {'apiBranch': 'emails', 'apiEntity': 'email'},
            'Event': {'apiBranch': 'events', 'apiEntity': 'event'},
            'Incident': {'apiBranch': 'incidents', 'apiEntity': 'incident'},
            'Intrusion Set': {'apiBranch': 'intrusionSets', 'apiEntity': 'intrusionSet'},
            'Report': {'apiBranch': 'reports', 'apiEntity': 'report'},
            'Signature': {'apiBranch': 'signatures', 'apiEntity': 'signature'},
            'Threat': {'apiBranch': 'threats', 'apiEntity': 'threat'},
        }
