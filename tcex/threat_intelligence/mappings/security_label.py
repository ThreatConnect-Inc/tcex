# -*- coding: utf-8 -*-
"""ThreatConnect TI Security Label"""

from .mappings import Mappings

# import local modules for dynamic reference
module = __import__(__name__)


class SecurityLabel(Mappings):
    """Unique API calls for SecurityLabel API Endpoints"""

    def __init__(self, tcex, name, **kwargs):
        """

        Args:
            tcex:
            name:
            **kwargs:
        """
        super().__init__(
            tcex,
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
        """Indicates that this is a security label object

        Returns:

        """
        return True

    def can_create(self):
        """If the name has been provided returns that the SecurityLabel can be created, otherwise
        returns that the SecurityLabel cannot be created.

        Returns:

        """
        if self._data.get('name'):
            return True
        return False

    def add_key_value(self, key, value):
        """Converts the value and adds it as a data field.

          Args:
              key:
              value:
          """
        self._data[key] = value

    def name(self, name):
        """Updates the security labels name.

        Args:
            name:
        """
        self._data['name'] = name
        data = {'name': name}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def color(self, color):
        """Updates the security labels color.

        Args:
            color:

        """
        self._data['color'] = color
        data = {'color': color}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def description(self, description):
        """Updates the security labels description.

        Args:
            description:
        """
        self._data['description'] = description
        data = {'description': description}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )

    def date_added(self, date_added):
        """Updates the security labels date_added

        Args:
            date_added: Converted to %Y-%m-%dT%H:%M:%SZ date format
        """
        date_added = self._utils.datetime.format_datetime(
            date_added, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

        self._data['dateAdded'] = date_added
        data = {'dateAdded': date_added}
        return self._tc_requests.update(
            self.api_type, self.api_branch, self.unique_id, data, owner=self.owner
        )
