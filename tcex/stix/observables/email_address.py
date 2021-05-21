"""Parser for STIX Email Address Object.

see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070690
"""
# standard library
from typing import Iterable, Union

# third-party
from stix2 import EmailAddress

# first-party
from tcex.stix.model import StixModel  # pylint: disable=cyclic-import


class StixEmailAddressObject(StixModel):
    """Parser for STIX Email Address Object.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070690
    """

    # pylint: disable=arguments-differ
    def produce(self, tc_data: Union[list, dict], **kwargs) -> Iterable[EmailAddress]:
        """Produce STIX 2.0 JSON object from TC API response."""
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'address'

        parse_map = {
            'type': 'email-addr',
            'spec_version': '2.1',
            'id': '@.id',
            'value': f'@."{indicator_field}"',
        }

        yield from (EmailAddress(**stix_data) for stix_data in self._map(tc_data, parse_map))

    # pylint: disable=arguments-differ
    def consume(self, stix_data: Union[list, dict]):
        """Produce a ThreatConnect object from a STIX 2.0 JSON object."""
        parse_map = {
            'type': 'EmailAddress',
            'address': '@.value',
            'confidence': '@.confidence',
            'xid': '@.id',
            'attributes': [{'type': 'External ID', 'value': '@.id'}],
        }
        parse_map.update(self.default_map)

        yield from self._map(
            stix_data,
            parse_map,
        )
