"""TcEx Framework Module"""

# standard library
import logging

# third-party
from pydantic import BaseModel

# first-party
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property

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

    @cached_property
    def naics_tags_name_id(self) -> dict[str, list[NAICSTag]]:
        """Return a dict of MitreTags keyed by name."""
        naics_tags = {}
        for tag in self._naics_tags.values():
            naics_tags.setdefault(tag.name.lower(), []).append(NAICSTag(id=tag.id, name=tag.name))

        return naics_tags

    def get_by_name(self, name: str, default: list[str] | None = None) -> list[str] | None:
        """Return the tag id for the provided name."""
        naics_tags = self.naics_tags_name_id.get(name.lower(), [])
        tags = []
        for tag in naics_tags:
            tags.append(tag.formatted)
        if not tags and self.verbose:
            self.log.warning(f'No NAICS match found for {name}.')
        return tags or default

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
        tag = self._naics_tags.get(parent)
        if tag:
            tags.append(tag.formatted)

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
