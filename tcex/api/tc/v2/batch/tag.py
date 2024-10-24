"""TcEx Framework Module"""

# standard library
import json
from collections.abc import Callable


class Tag:
    """ThreatConnect Batch Tag Object"""

    __slots__ = ['_tag_data', '_valid']

    def __init__(self, name: str, formatter: Callable[[str], str] | None = None):
        """Initialize instance properties.

        Args:
            name: The value for this tag.
            formatter: A callable that take a tag value and returns a formatted tag.
        """
        if formatter is not None:
            name = formatter(name)
        self._tag_data = {'name': name}
        # is tag not null or ''
        self._valid = True
        if not name:
            self._valid = False

    @property
    def data(self) -> dict:
        """Return Tag data."""
        return self._tag_data

    @property
    def name(self) -> str:
        """Return Tag name."""
        return self._tag_data.get('name')  # type: ignore

    @property
    def valid(self) -> bool:
        """Return valid data."""
        return self._valid

    def __str__(self) -> str:
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)
