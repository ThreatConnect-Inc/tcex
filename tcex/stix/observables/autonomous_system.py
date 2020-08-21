"""Parser for STIX AS Object.

see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070683
"""
# standard library
from typing import Iterable, Union

# third-party
from stix2 import AutonomousSystem

# first-party
from tcex.stix.model import StixModel  # pylint: disable=cyclic-import


class StixASObject(StixModel):
    """Parser for STIX AS Object.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070683
    """

    def produce(self, tc_data: Union[list, dict], **kwargs) -> Iterable[AutonomousSystem]:
        """Produce STIX 2.0 JSON object from TC API response."""
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'AS Number'

        parse_map = {
            'type': 'autonomous-system',
            'spec_version': '2.1',
            'id': '@.id',
            'number': f'@."{indicator_field}"',
        }

        yield from (AutonomousSystem(**stix_data) for stix_data in self._map(tc_data, parse_map))

    def consume(self, stix_data: Union[list, dict]):
        """Produce a ThreatConnect object from a STIX 2.0 JSON object."""
        parse_map = {
            'type': 'ASN',
            'summary': '@.number',
            'xid': '@.id',
            'attributes': [{'type': 'External ID', 'value': '@.id'}],
        }

        def _convert_summary_to_str(data):
            data['summary'] = str(data.get('summary'))
            return data

        yield from map(_convert_summary_to_str, self._map(stix_data, parse_map))
