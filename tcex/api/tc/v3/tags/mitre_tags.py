"""TcEx Framework Module"""

# standard library
import logging
import re

# third-party
from pydantic import BaseModel

# first-party
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class MitreTag(BaseModel):
    """MitreTag Class"""

    id: str
    name: str

    @property
    def formatted(self):
        """Return the formatted tag."""
        return f'{self.id} - {self.name}'


class MitreTags:
    """MitreTags Class"""

    def __init__(self, mitre_tags: dict[str, str]):
        """Initialize instance properties."""
        self._mitre_tags = {id_: MitreTag(id=id_, name=name) for id_, name in mitre_tags.items()}
        self.log = _logger

    @cached_property
    def mitre_tags_name_id(self):
        """Return a dict of MitreTags keyed by name."""
        mitre_tags = {}
        for tag in self._mitre_tags.values():
            titles = tag.name.split(': ')

            key = titles[1].strip() if len(titles) > 1 else tag.name
            mitre_tags[key.lower()] = MitreTag(id=tag.id, name=tag.name)

        return mitre_tags

    def get_by_name(self, name: str) -> str | None:
        """Return the tag id for the provided name."""
        mitre_tag = self.mitre_tags_name_id.get(name.lower())
        if mitre_tag is None:
            self.log.warning(f'No Mitre match found for {name}.')
            return None
        return mitre_tag.formatted

    def get_by_id(self, id_: str) -> str:
        """Return the tag name for the provided id."""
        mitre_tag = self._mitre_tags.get(id_)
        if mitre_tag is None:
            self.log.warning(f'No Mitre match found for {id_}, returning id unformatted.')
            return id_
        return mitre_tag.formatted

    def get_by_id_regex(self, value: str):
        r"""Get the appropriate MitreTag using the (T\d+(?:\.\d+)?) regex."""
        matches = re.findall(r'(T\d+(?:\.\d+)?)', value)
        if not matches:
            self.log.warning(f'No Mitre matches found for {value}')
            return None
        if len(matches) > 1:
            self.log.warning(f'Multiple Mitre matches found for {value}: {matches}')
            return None
        return self.get_by_id(matches[0])
