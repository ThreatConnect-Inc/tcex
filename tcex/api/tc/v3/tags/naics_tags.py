"""TcEx Framework Module"""

# standard library
import logging

# third-party
from pydantic import BaseModel

# first-party
from tcex.logger.trace_logger import TraceLogger

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class NAICSTag(BaseModel):
    """NAICTag Class"""

    id: str
    name: str

    @property
    def formatted(self):
        """Return the formatted tag."""
        return f'NAICS: {self.id} - {self.name}'


class NAICSTags:
    """NAICTags Class"""

    def __init__(self, naics_tags: dict[str, str], verbose: bool = False):
        """Initialize instance properties."""
        self._naics_tags = {id_: NAICSTag(id=id_, name=name) for id_, name in naics_tags.items()}
        self.verbose = verbose
        self.log = _logger

    def get_by_id(self, id_: str | int, default=None) -> str | None:
        """Return the tag name for the provided id."""
        if isinstance(id_, int):
            id_ = str(id_)
        tag = self._naics_tags.get(id_)
        if not tag:
            if self.verbose is True:
                self.log.warning(f'No NAICS match found for {id_}.')
            return default
        return tag.formatted


    def get_all_by_id(self, id_: str | int, default=None) -> list[str] | None:
        """Return the tag name for the provided id."""
        id_ = str(id_)

        if not self._naics_tags.get(id_):
            if self.verbose:
                self.log.warning(f'No NAICS match found for {id_}.')
            return default

        parent = id_[:2]
        tags = []
        if self._naics_tags.get(parent):
            tags.append(self._naics_tags.get(parent).formatted)

        remainder = id_[2:]
        if not remainder:
            if not tags and self.verbose:
                self.log.warning(f'No NAICS match found for {id_}.')
            return tags or default

        current_id = parent
        for subtype in remainder:
            current_id += subtype
            if tag := self._naics_tags.get(current_id):
                tags.append(tag.formatted)
        if not tags and self.verbose:
            self.log.warning(f'No NAICS match found for {id_}.')
        return tags or default
