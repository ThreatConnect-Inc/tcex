# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""

from tcex.tcex_ti.mappings.tcex_ti_mappings import TIMappings

# import local modules for dynamic reference
module = __import__(__name__)


class SecurityLabel(TIMappings):
    def __init__(self, tcex, name, **kwargs):
        super(SecurityLabel, self).__init__(tcex, 'SecurityLabel', **kwargs)
        self._data['type'] = 'securityLabels'
        self._data['sub_type'] = None
        self._data['name'] = name

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    def can_create(self):
        if self._data.get('name'):
            return True
        return False
    
    def add_key_value(self, key, value):
        self._data[key] = value

    def name(self, name):
        """Return Email to."""
        self._data['name'] = name
        request = self._base_request()
        request['name'] = name
        return self._tc_requests.update(request)

    def color(self, color):
        """Return Email to."""
        self._data['color'] = color
        request = self._base_request()
        request['color'] = color
        return self._tc_requests.update(request)

    def description(self, description):
        """Return Email to."""
        self._data['description'] = description
        request = self._base_request()
        request['description'] = description
        return self._tc_requests.update(request)

    def date_added(self, date_added):
        """Return Email to."""
        date_added = self._utils.format_datetime(
            date_added, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

        self._data['dateAdded'] = date_added
        request = self._base_request()
        request['dateAdded'] = date_added
        return self._tc_requests.update(request)
