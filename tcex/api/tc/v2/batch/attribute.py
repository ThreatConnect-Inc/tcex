"""TcEx Framework Module"""

# standard library
import json
from collections.abc import Callable

# first-party
from tcex.util import Util


class Attribute:
    """ThreatConnect Batch Attribute Object"""

    __slots__ = ['_attribute_data', '_valid', 'util']

    def __init__(
        self,
        attr_type: str,
        attr_value: str,
        displayed: bool = False,
        source: str | None = None,
        formatter: Callable[[str], str] | None = None,
    ):
        """Initialize instance properties.

        Args:
            attr_type: The ThreatConnect defined attribute type.
            attr_value: The value for this attribute.
            displayed: If True the supported attribute will be marked for display.
            source: The source value for this attribute.
            formatter: A callable that take a single attribute
                value and return a single formatted value.
        """
        self._attribute_data: dict[str, bool | str] = {'type': attr_type}
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

        # properties
        self.util = Util()

    @property
    def data(self) -> dict:
        """Return Attribute data."""
        return self._attribute_data

    @property
    def displayed(self) -> bool:
        """Return Attribute displayed."""
        return self.util.to_bool(self._attribute_data.get('displayed') or False)

    @displayed.setter
    def displayed(self, displayed: bool):
        """Set Attribute displayed."""
        self._attribute_data['displayed'] = displayed

    @property
    def source(self) -> str | None:
        """Return Attribute source."""
        return str(self._attribute_data.get('source'))

    @source.setter
    def source(self, source: str):
        """Set Attribute source."""
        self._attribute_data['source'] = source

    @property
    def type(self) -> str:
        """Return attribute value."""
        return str(self._attribute_data['type'])

    @property
    def valid(self) -> bool:
        """Return valid value."""
        return self._valid

    @property
    def value(self) -> bool | str | None:
        """Return attribute value."""
        return self._attribute_data['value']

    def __str__(self) -> str:
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)
