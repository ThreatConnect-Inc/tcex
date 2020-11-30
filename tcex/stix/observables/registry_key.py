"""ThreatConnect STIX module"""
# standard library
from typing import Union

# third-party
from stix2 import WindowsRegistryKey

# first-party
from tcex.stix.model import StixModel  # pylint: disable=cyclic-import


class StixRegistryKeyObject(StixModel):
    """STIX Threat Actor object."""

    # pylint: disable=arguments-differ
    def consume(self, stix_data: Union[list, dict]):
        """Convert STIX Windows Registry Key Cyber Observables to ThreatConnect Indicators.

        Args:
            stix_data: STIX Windows Registry Key Cyber Observables.

        Yields:
            ThreatConnect registry key indicators.
        """
        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        for data in stix_data:
            mapper = {
                'type': 'Registry Key',
                'Key Name': '@.key',
                'xid': '@.id',
                'confidence': '@.confidence',
                'attributes': [{'type': 'External ID', 'value': '@.id'}],
            }
            mapper.update(self.default_map)
            if not data.get('values'):
                yield from self._map(data, mapper)
            else:
                for i in range(len(data.get('values'))):
                    mapper['Value Name'] = f'@.values[{i}].name'
                    mapper['Value Type'] = f'@.values[{i}].data_type'
                    mapper['attributes'].append(
                        {'type': 'Value Data', 'value': f'@.values[{i}].data'}
                    )
                    yield from self._map(data, mapper)

    # pylint: disable=arguments-differ
    def produce(self, tc_data: Union[list, dict], **kwargs):
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
            'value': [{'name': '@.Value Name', 'data': '', 'data_type': '@.Value Type'}],
            'spec_version': '2.1',
            'type': 'windows-registry-key',
        }

        yield from (WindowsRegistryKey(**stix_data) for stix_data in self._map(tc_data, mapper))
