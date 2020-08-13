"""ThreatConnect STIX module"""
from typing import Union
from .model import StixModel
from stix2 import IPv6Address


class StixIPv6Object(StixModel):
    """STIX Threat Actor object."""

    def consume(self, stix_data: Union[list, dict]):
        mapper = {
            'type': 'Address',
            'summary': '@.value',
            'attributes': {'type': 'External Id', 'value': '@.id'}
        }

        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        yield from self._map(stix_data, mapper)

    def produce(self, tc_data: Union[list, dict]):
        """Produce STIX 2.0 JSON object from TC API response.

        .. code:: json

            {
              "type": "ipv6-addr",
              "spec_version": "2.1",
              "id": "ipv6-addr--1e61d36c-a16c-53b7-a80f-2a00161c96b1",
              "value": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
            }
        """
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'ip'

        mapper = {
            'id': '@.id',
            'value': f'@.{indicator_field}',
            'spec_version': '2.1',
            'type': 'ipv6-addr'
        }

        for stix_data in self._map(tc_data, mapper):
            yield IPv6Address(**stix_data)

