"""ThreatConnect STIX module"""
from typing import Union
from .model import StixModel
import jmespath
from stix2.v21 import (
    ThreatActor,
    Identity,
    AttackPattern,
    Campaign,
    IntrusionSet,
    Relationship,
    ExternalReference,
    Bundle,
)


class StixIPv4Object(StixModel):
    """STIX Threat Actor object."""

    def consume(self, stix_data: Union[list, dict]):
        mapper = {
            'type': 'Address',
            'summary': '@.value',
            'attributes': {'type': 'External Id', 'value': '@.id'}
        }

        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        for tc_data in self._map(stix_data, mapper):
            return tc_data

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
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'ip'

        mapper = {
            'id': '@.id',
            'value': f'@.{indicator_field}',
            'spec_version': '2.1',
            'type': 'ipv4-addr'
        }

        tc_data = list(tc_data)

        for stix_data in self._map(tc_data, mapper):
            return ThreatActor(**stix_data)

