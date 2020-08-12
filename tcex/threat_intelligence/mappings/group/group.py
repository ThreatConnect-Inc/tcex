# -*- coding: utf-8 -*-
"""ThreatConnect TI Group"""
# standard library
from urllib.parse import quote_plus

from ..mappings import Mappings


class Group(Mappings):
    """Unique API calls for Group API Endpoints"""

    def __init__(self, tcex, **kwargs):
        """Initialize Class properties."""
        super().__init__(
            tcex,
            'Group',
            'groups',
            kwargs.pop('sub_type', None),
            kwargs.pop('api_entity', 'group'),
            kwargs.pop('api_branch', None),
            kwargs.pop('owner', None),
        )
        self.name = None

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @property
    def as_entity(self):
        """Return the entity representation of the Indicator."""
        return {
            'type': self.api_sub_type,
            'value': self.name,
            'id': int(self.unique_id) if self.unique_id else None,
        }

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
        """Return True if group can be create."""
        return self.data.get('name') is not None

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
        elif key in ['unique_id', 'id']:
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
        """Set the unique id of the Group."""
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
