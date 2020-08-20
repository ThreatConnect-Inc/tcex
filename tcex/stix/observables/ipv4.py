"""ThreatConnect STIX module"""
# standard library
from typing import Union

# first-party
from tcex.stix.model import StixModel


class StixIPv4Object(StixModel):
    """STIX Threat Actor object."""

    def consume(self, stix_data: Union[list, dict]):

        mapper_ip = {
            'type': 'Address',
            'summary': '@.value',
            'attributes': {'type': 'External Id', 'value': '@.id'},
        }

        mapper_cider = {
            'type': 'CIDR',
            'summary': '@.value',
            'attributes': {'type': 'External Id', 'value': '@.id'},
        }

        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        for data in stix_data:
            if data.get('type') == 'ipv4-addr':
                cidr_parts = data.get('value', '').split('/')
                cidr_suffix = cidr_parts[1] if len(cidr_parts) > 1 else '32'
                if cidr_suffix == '32':
                    yield from self._map(data, mapper_ip)
                else:
                    yield from self._map(data, mapper_cider)

            if data.get('type') == 'ipv6-addr':
                cidr_parts = data.get('value', '').split('/')
                cidr_suffix = cidr_parts[1] if len(cidr_parts) > 1 else '128'
                if cidr_suffix == '128':
                    yield from self._map(data, mapper_ip)
                else:
                    yield from self._map(data, mapper_cider)

    def produce(self, tc_data: Union[list, dict]):
        """Produce STIX 2.0 JSON object from TC API response.

        .. code:: json

            {
              "type": "ipv4-addr",
              "spec_version": "2.1",
              "id": "ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd",
              "value": "198.51.100.3"
            }
        """
        if isinstance(tc_data, dict):
            tc_data = [tc_data]

        for data in tc_data:
            if 'ip' in data or data.get('type') == 'Address':
                yield from self._produce_address(data)
            else:
                yield from self._produce_cidr(data)

    def _produce_cidr(self, tc_data: dict):
        indicator_field = 'summary' if 'summary' in tc_data else 'block'

        ip_type = 'ipv6' if ':' in tc_data.get(indicator_field, '') else 'ipv4'

        yield from self._map(
            tc_data,
            {
                'id': '@.id',
                'value': f'@.{indicator_field}',
                'spec_version': '2.1',
                'type': f'{ip_type}-addr',
            },
        )

    def _produce_address(self, tc_data: dict):
        indicator_field = 'summary' if 'summary' in tc_data else 'ip'

        ip_type = 'ipv6' if ':' in tc_data.get(indicator_field, '') else 'ipv4'

        yield from self._map(
            tc_data,
            {
                'id': '@.id',
                'value': f'@.{indicator_field}',
                'spec_version': '2.1',
                'type': f'{ip_type}-addr',
            },
        )
