# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""
# standard library
import json


class Tag:
    """ThreatConnect Batch Tag Object"""

    __slots__ = ['_tag_data', '_valid']

    def __init__(self, name, formatter=None):
        """Initialize Class Properties.

        Args:
            name (str): The value for this tag.
            formatter (method, optional): A method that take a tag value and returns a
                formatted tag.
        """
        if formatter is not None:
            name = formatter(name)
        self._tag_data = {'name': name}
        # is tag not null or ''
        self._valid = True
        if not name:
            self._valid = False

    @property
    def data(self):
        """Return Tag data."""
        return self._tag_data

    @property
    def name(self):
        """Return Tag name."""
        return self._tag_data.get('name')

    @property
    def valid(self):
        """Return valid data."""
        return self._valid

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)
