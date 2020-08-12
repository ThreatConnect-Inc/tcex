# -*- coding: utf-8 -*-
"""ThreatConnect SecurityLabel Object"""
# standard library
import json


class SecurityLabel:
    """ThreatConnect Batch SecurityLabel Object."""

    __slots__ = ['_label_data']

    def __init__(self, name, description=None, color=None):
        """Initialize Class Properties.

        Args:
            name (str): The value for this security label.
            description (str): A description for this security label.
            color (str): A color (hex value) for this security label.
        """
        self._label_data = {'name': name}
        # add description if provided
        if description is not None:
            self._label_data['description'] = description
        if color is not None:
            self._label_data['color'] = color

    @property
    def color(self):
        """Return Security Label color."""
        return self._label_data.get('color')

    @color.setter
    def color(self, color):
        """Set Security Label color."""
        self._label_data['color'] = color

    @property
    def data(self):
        """Return Security Label data."""
        return self._label_data

    @property
    def description(self):
        """Return Security Label description."""
        return self._label_data.get('description')

    @description.setter
    def description(self, description):
        """Set Security Label description."""
        self._label_data['description'] = description

    @property
    def name(self):
        """Return Security Label name."""
        return self._label_data.get('name')

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)
