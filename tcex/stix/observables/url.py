"""ThreatConnect STIX module"""
# standard library
from typing import Union

# third-party
from stix2 import URL

# first-party
from tcex.stix.model import StixModel  # pylint: disable=cyclic-import


class StixURLObject(StixModel):
    """STIX Threat Actor object."""

    # pylint: disable=arguments-differ
    def consume(self, stix_data: Union[list, dict]):
        """Parse a STIX URL Object into a ThreatConnect URL Indicator."""
        mapper = {
            'type': 'URL',
            'text': '@.value',
            'xid': '@.id',
            'confidence': '@.confidence',
            'attributes': [{'type': 'External ID', 'value': '@.id'}],
        }
        mapper.update(self.default_map)

        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        yield from self._map(stix_data, mapper)

    # pylint: disable=arguments-differ
    def produce(self, tc_data: Union[list, dict], **kwargs):
        """Produce STIX 2.0 JSON object from TC API response.

        .. code:: json

           {
              "type": "url",
              "spec_version": "2.1",
              "id": "url--c1477287-23ac-5971-a010-5c287877fa60",
              "value": "https://example.com/research/index.html"
            }
        """
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'text'

        mapper = {
            'id': '@.id',
            'value': f'@.{indicator_field}',
            'spec_version': '2.1',
            'type': 'url',
        }

        for stix_data in self._map(tc_data, mapper):
            yield URL(**stix_data)
