"""TcEx Framework Module"""

# standard library
import logging
import re

# third-party
from pydantic import BaseModel
from requests import Session

# first-party
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property_filesystem import cached_property_filesystem

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class MitreTag(BaseModel):
    """Model for a single MITRE ATT&CK tag.

    Attributes:
        id: The MITRE technique id (e.g., ``T1205.001``).
        name: The technique name (e.g., ``Traffic Signaling: Port Knocking``).
    """

    id: str
    name: str

    @property
    def formatted(self) -> str:
        """Return the formatted tag.

        Returns:
            The id and name joined with `` - `` (e.g.,
            ``T1205.001 - Traffic Signaling: Port Knocking``).
        """
        return f'{self.id} - {self.name}'


class MitreTags:
    """Lookup service for MITRE ATT&CK tags retrieved from the ThreatConnect v3 API."""

    def __init__(self, session_tc: Session, verbose: bool = False):
        """Initialize instance properties.

        Args:
            session_tc: An authenticated requests session for the ThreatConnect API.
            verbose: If True, log warnings when tag lookups fail to find a match.
        """
        self.session_tc = session_tc
        self.verbose = verbose
        self.log = _logger

    @cached_property_filesystem(ttl=86400)
    def _mitre_tags(self) -> dict[str, MitreTag]:
        """Fetch raw MITRE tags from the ThreatConnect v3 API.

        Returns:
            A dict keyed by technique id with the MitreTag model as value.

        Raises:
            Exception: Re-raised after logging if the API request fails.
        """
        try:
            # no pagination is needed as there are only ~700 mitre tags currently
            params = {'resultLimit': 10_000, 'tql': 'techniqueId NE "null"'}
            results = self.session_tc.get('/v3/tags', params=params)
            if not results.ok:
                ex_msg = f'Error fetching Mitre Tags: {results.text}'
                raise RuntimeError(ex_msg)  # noqa: TRY301

            tags = results.json().get('data', [])
            return {
                str(tag.get('techniqueId')): MitreTag(
                    id=tag.get('techniqueId'), name=tag.get('name')
                )
                for tag in tags
            }
        except Exception:
            self.log.exception('Error downloading Mitre Tags')
            raise

    @cached_property_filesystem(ttl=86400)
    def mitre_tags_name_id(self) -> dict[str, MitreTag]:
        """Return MITRE tags keyed by lowercase sub-technique name.

        For tags whose name contains ``": "`` (e.g., ``Traffic Signaling: Port Knocking``),
        the key is the portion after the colon (``port knocking``).  Otherwise the full
        name is used.

        Returns:
            A dict keyed by lowercase name with ``MitreTag`` instances as values.
        """
        mitre_tags: dict[str, MitreTag] = {}
        for tag in self._mitre_tags.values():
            titles = tag.name.split(': ')

            key = titles[1].strip() if len(titles) > 1 else tag.name
            mitre_tags[key.lower()] = MitreTag(id=tag.id, name=tag.name)

        return mitre_tags

    def get_by_name(self, name: str, default: str | None = None) -> str | None:
        """Return the formatted MITRE tag for the provided sub-technique name.

        Args:
            name: The sub-technique name to look up (case-insensitive).
            default: Value returned when no match is found.

        Returns:
            The formatted tag string, or *default* if no match is found.
        """
        mitre_tag = self.mitre_tags_name_id.get(name.lower())
        if mitre_tag is None:
            if self.verbose is True:
                self.log.warning(f'No Mitre match found for {name}.')
            return default
        return mitre_tag.formatted

    def get_by_id(self, id_: str, default: str | None = None) -> str | None:
        """Return the formatted MITRE tag for the provided technique id.

        Args:
            id_: The technique id to look up (e.g., ``T1205``, ``T1205.001``).
            default: Value returned when no match is found.

        Returns:
            The formatted tag string, or *default* if no match is found.
        """
        mitre_tag = self._mitre_tags.get(str(id_).upper())
        if mitre_tag is None:
            if self.verbose is True:
                self.log.warning(f'No Mitre match found for {id_}, returning id unformatted.')
            return default
        return mitre_tag.formatted

    def get_by_id_regex(self, value: str, default: str | None = None) -> str | None:
        r"""Return the formatted MITRE tag by extracting a technique id from *value* via regex.

        The pattern ``([Tt]\d+(?:\.\d+)?)`` is used to find technique ids within the
        input string.  Exactly one match is required; zero or multiple matches return
        *default*.

        Args:
            value: A string that may contain a MITRE technique id.
            default: Value returned when no single match is found.

        Returns:
            The formatted tag string, or *default* if no single match is found.
        """
        matches = re.findall(r'([Tt]\d+(?:\.\d+)?)', value)
        if not matches:
            if self.verbose is True:
                self.log.warning(f'No Mitre matches found for {value}')
            return default
        if len(matches) > 1:
            if self.verbose is True:
                self.log.warning(f'Multiple Mitre matches found for {value}: {matches}')
            return default
        return self.get_by_id(matches[0], default)
