# -*- coding: utf-8 -*-
"""ThreatConnect TI Group"""
from urllib.parse import quote_plus
from ..mappings import Mappings


class Group(Mappings):
    """Unique API calls for Group API Endpoints"""

    def __init__(self, tcex, sub_type, api_entity, api_branch, owner=None, **kwargs):
        """Initialize Class properties."""
        super().__init__(tcex, 'Group', 'groups', sub_type, api_entity, api_branch, owner)
        self.name = None

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @staticmethod
    def is_group():
        """Return True if object is a group."""
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
        """Return True if registry key can be create."""
        return self.data.get('name') is True

    def add_key_value(self, key, value):
        """Convert the value and adds it as a data field.

        Args:
            key:
            value:
        """
        key = self._metadata_map.get(key, key)
        if key in ['dateAdded', 'eventDate', 'firstSeen', 'publishDate']:
            self._data[key] = self._utils.datetime.format_datetime(
                value, date_format='%Y-%m-%dT%H:%M:%SZ'
            )
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
        if key == 'name':
            self.name = value

    @property
    def name(self):
        """Return the Group name."""
        return self._data.get('name')

    @name.setter
    def name(self, name):
        """Set the Group name."""
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
