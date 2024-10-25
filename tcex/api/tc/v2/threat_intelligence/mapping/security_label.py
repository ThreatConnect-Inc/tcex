"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.mapping import Mapping

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence

# import local modules for dynamic reference
module = __import__(__name__)


class SecurityLabel(Mapping):
    """Unique API calls for SecurityLabel API Endpoints"""

    def __init__(self, ti: 'ThreatIntelligence', name, **kwargs):
        """."""
        super().__init__(
            ti,
            main_type='SecurityLabel',
            api_type='securitylabels',
            sub_type=None,
            api_entity='securityLabel',
            api_branch=None,
            owner=kwargs.pop('owner', None),
        )
        self._data['type'] = 'securityLabels'
        self._data['sub_type'] = None
        self._data['name'] = name

        for arg, value in kwargs.items():
            self.add_key_value(arg, value)

    @property
    def as_entity(self):
        """Return the object as an entity."""
        return {}

    @staticmethod
    def is_security_label():
        """Return indication that this is a security label object."""
        return True

    def can_create(self):
        """Return true if security label can be created."""
        if self._data.get('name'):
            return True
        return False

    def add_key_value(self, key, value):
        """Convert the value and adds it as a data field."""
        self._data[key] = value

    def name(self, name):
        """Update the security labels name."""
        self._data['name'] = name
        data = {'name': name}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def color(self, color):
        """Update the security labels color."""
        self._data['color'] = color
        data = {'color': color}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def description(self, description):
        """Update the security labels description."""
        self._data['description'] = description
        data = {'description': description}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def date_added(self, date_added):
        """Update the security labels date_added.

        Args:
            date_added: Converted to %Y-%m-%dT%H:%M:%SZ date format
        """
        date_added = self.util.any_to_datetime(date_added).strftime('%Y-%m-%dT%H:%M:%SZ')

        self._data['dateAdded'] = date_added
        data = {'dateAdded': date_added}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )
