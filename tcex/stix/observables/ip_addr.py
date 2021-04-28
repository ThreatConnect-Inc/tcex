"""ThreatConnect STIX module"""
# standard library
from typing import Union

# third-party
from stix2 import IPv6Address

# first-party
from tcex.stix.model import StixModel  # pylint: disable=cyclic-import


class StixIPBase(StixModel):
    """Base class for IPv4 and IPv6 objects."""

    def do_consume(self, stix_data: Union[list, dict], full_block_size: int):
        """Convert a STIX object to a TC Address or CIDR.

        Args:
            stix_data: the data to convert
            full_block_size: the size of a full block in the respective CIDR
        """
        mapper_ip = {
            'type': 'Address',
            'ip': '@.value',
            'xid': '@.id',
            'confidence': '@.confidence',
            'attributes': [{'type': 'External ID', 'value': '@.id'}],
        }
        mapper_ip.update(self.default_map)

        mapper_cider = {
            'confidence': '@.confidence',
            'type': 'CIDR',
            'block': '@.value',
            'xid': '@.id',
            'attributes': [{'type': 'External ID', 'value': '@.id'}],
        }
        mapper_cider.update(self.default_map)

        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        for data in stix_data:
            cidr_parts = data.get('value', '').split('/')
            cidr_suffix = cidr_parts[1] if len(cidr_parts) > 1 else str(full_block_size)
            if cidr_suffix == str(full_block_size):
                yield from self._map(data, mapper_ip)
            else:
                yield from self._map(data, mapper_cider)


class StixIPv4Object(StixIPBase):
    """STIX Threat Actor object."""

    # pylint: disable=arguments-differ
    def consume(self, stix_data: Union[list, dict]):
        """Convert STIX IPv4-addr Cyber Observables to ThreatConnect indicators.

        Args:
            stix_data: One or more STIX ipv4-addr cyber observables.

        Yields:
            ThreatConnect addresses or CIDRs.
        """
        yield from super().do_consume(stix_data, 32)

    # pylint: disable=arguments-differ
    def produce(self, tc_data: Union[list, dict], **kwargs):
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

        parse_map = {
            'id': '@.id',
            'summary': f'@.{indicator_field}',
            'spec_version': '2.1',
            'type': f'{ip_type}-addr',
        }

        yield from self._map(
            tc_data,
            parse_map,
        )

    def _produce_address(self, tc_data: dict):
        indicator_field = 'summary' if 'summary' in tc_data else 'ip'

        ip_type = 'ipv6' if ':' in tc_data.get(indicator_field, '') else 'ipv4'

        parse_map = {
            'id': '@.id',
            'summary': f'@.{indicator_field}',
            'spec_version': '2.1',
            'type': f'{ip_type}-addr',
        }

        yield from self._map(
            tc_data,
            parse_map,
        )


class StixIPv6Object(StixIPBase):
    """STIX Threat Actor object."""

    # pylint: disable=arguments-differ
    def consume(self, stix_data: Union[list, dict]):
        """Convert STIX IPv6-addr Cyber Observables to ThreatConnect indicators.

        Args:
            stix_data: One or more STIX ipv6-addr cyber observables.

        Yields:
            ThreatConnect addresses or CIDRs.
        """
        yield from super().do_consume(stix_data, 128)

    # pylint: disable=arguments-differ
    def produce(self, tc_data: Union[list, dict], **kwargs):
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
            'summary': f'@.{indicator_field}',
            'spec_version': '2.1',
            'type': 'ipv6-addr',
        }

        yield from (IPv6Address(**stix_data) for stix_data in self._map(tc_data, mapper))
