"""TcEx Framework Module"""

# standard library
import json


class SecurityLabel:
    """ThreatConnect Batch SecurityLabel Object."""

    __slots__ = ['_label_data']

    def __init__(self, name: str, description: str | None = None, color: str | None = None):
        """Initialize instance properties.

        Args:
            name: The value for this security label.
            description: A description for this security label.
            color: A color (hex value) for this security label.
        """
        self._label_data = {'name': name}
        # add description if provided
        if description is not None:
            self._label_data['description'] = description
        if color is not None:
            self._label_data['color'] = color

    @property
    def color(self) -> str | None:
        """Return Security Label color."""
        return self._label_data.get('color')

    @color.setter
    def color(self, color: str):
        """Set Security Label color."""
        self._label_data['color'] = color

    @property
    def data(self) -> dict:
        """Return Security Label data."""
        return self._label_data

    @property
    def description(self) -> str | None:
        """Return Security Label description."""
        return self._label_data.get('description')

    @description.setter
    def description(self, description: str):
        """Set Security Label description."""
        self._label_data['description'] = description

    @property
    def name(self) -> str:
        """Return Security Label name."""
        return self._label_data['name']

    def __str__(self) -> str:
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)
