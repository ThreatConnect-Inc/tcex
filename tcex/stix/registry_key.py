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


class StixRegistryKeyObject(StixModel):
    """STIX Threat Actor object."""

    def consume(self, stix_data: Union[list, dict]):
        mapper = {
            'type': 'Registry Key',
            'summary': '@.name',
            'attributes': {
                'type': 'External Id', 'value': '@.id'
                # 'type': 'Value Data', 'value': '@.id'
            }
        }

        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        for tc_data in self._map(stix_data, mapper):
            return tc_data

    def produce(self, tc_data: Union[list, dict]):
        """Produce STIX 2.0 JSON object from TC API response.

        .. code:: json

            {
              "type": "windows-registry-key",
              "spec_version": "2.1",
              "id": "windows-registry-key--2ba37ae7-2745-5082-9dfd-9486dad41016",
              "key": "hkey_local_machine\\system\\bar\\foo",
              "values": [
                {
                  "name": "Foo",
                  "data": "qwerty",
                  "data_type": "REG_SZ"
                },
                {
                  "name": "Bar",
                  "data": "42",
                  "data_type": "REG_DWORD"
                }
              ]
            }
        """
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            for data in tc_data:
                summary = data.get('summary').split(':')
                data['Key Name'] = summary[0].trim()
                data['Value Name'] = summary[1].trim()
                data['Value Type'] = summary[2].trim()
                del data['summary']

        mapper = {
            'id': '@.id',
            'key': '@.Key Name',
            'value': [
                {
                    'name': '@.Value Name',
                    'data': '',
                    'data_type': '@.Value Type'
                }
            ],
            'spec_version': '2.1',
            'type': 'windows-registry-key'
        }

        for stix_data in self._map(tc_data, mapper):
            return stix_data
