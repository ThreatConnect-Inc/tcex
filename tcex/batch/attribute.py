# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""
# standard library
import json


class Attribute:
    """ThreatConnect Batch Attribute Object"""

    __slots__ = ['_attribute_data', '_valid']

    def __init__(self, attr_type, attr_value, displayed=False, source=None, formatter=None):
        """Initialize Class Properties.

        Args:
            attr_type (str): The ThreatConnect defined attribute type.
            attr_value (str): The value for this attribute.
            displayed (bool, default:false): If True the supported attribute will be marked for
                display.
            source (str, optional): The source value for this attribute.
            formatter (method, optional): A method that take a single attribute value and return a
                single formatted value.
        """
        self._attribute_data = {'type': attr_type}
        if displayed:
            self._attribute_data['displayed'] = displayed
        # format the value
        if formatter is not None:
            attr_value = formatter(attr_value)
        self._attribute_data['value'] = attr_value
        # add source if provided
        if source is not None:
            self._attribute_data['source'] = source
        # is attr_value not null or ''
        self._valid = True
        # check for None and '' value only.
        if attr_value in [None, '']:
            self._valid = False

    @property
    def data(self):
        """Return Attribute data."""
        return self._attribute_data

    @property
    def displayed(self):
        """Return Attribute displayed."""
        return self._attribute_data.get('displayed')

    @displayed.setter
    def displayed(self, displayed):
        """Set Attribute displayed."""
        self._attribute_data['displayed'] = displayed

    @property
    def source(self):
        """Return Attribute source."""
        return self._attribute_data.get('source')

    @source.setter
    def source(self, source):
        """Set Attribute source."""
        self._attribute_data['source'] = source

    @property
    def type(self):
        """Return attribute value."""
        return self._attribute_data.get('type')

    @property
    def valid(self):
        """Return valid value."""
        return self._valid

    @property
    def value(self):
        """Return attribute value."""
        return self._attribute_data.get('value')

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)
