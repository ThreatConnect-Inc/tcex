"""Parser for STIX Threat Actor Object.

see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070663
"""
# standard library
from typing import Union

# third-party
from stix2.v21 import ThreatActor

from .model import StixModel


class StixThreatActor(StixModel):
    """Parser for STIX Threat Actor Object.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070663
    """

    def consume(self, stix_data: Union[list, dict]):
        """Convert a STIX Threat Actor to a ThreatConnect Threat.

        Args:
            stix_data: One or more STIX Threat Actor objects.

        Yields:
            A ThreatConnect Threat for each STIX Threat Actor.
        """
        mapper = {
            'type': 'Threat',
            'summary': '@.name',
            'attributes': {'type': 'External Id', 'value': '@.id'},
        }

        if isinstance(stix_data, dict):
            stix_data = [stix_data]

        yield from self._map(stix_data, mapper)

    def produce(self, tc_data: Union[list, dict], **kwargs):
        """Produce STIX 2.0 JSON object from TC API response.

        .. code:: json

            {
              "id": 130292,
              "summary": "kpot",
              "ownerName": "TCI",
              "dateAdded": "2020-07-22T18:45:06Z",
              "webLink": "https://int-tc-01.tci.ninja/auth/threat/threat.xhtml?threat=130292",
              "attribute": [
                {
                  "id": 1098243,
                  "type": "Threat Type",
                  "value": "Malware Family",
                  "dateAdded": "2020-07-24T15:33:04Z",
                  "lastModified": "2020-07-24T15:33:04Z",
                  "displayed": false,
                  "xid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904:1098243"
                },
                {
                  "id": 1098242,
                  "type": "External ID",
                  "value": "eed6df9be6bdcc0b2ca2f88d7245cfa0",
                  "dateAdded": "2020-07-24T15:33:04Z",
                  "lastModified": "2020-07-24T15:33:04Z",
                  "displayed": false,
                  "xid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904:1098242"
                }
              ],
              "xid": "eed6df9be6bdcc0b2ca2f88d7245cfa0"
            }
        """
        mapper = {
            'id': '@.id',
            'created': '@.dateAdded',
            'modified': '@.dateAdded',
            'name': '@.name',
            # multiple groups
            # 'description': '[].attribute[?type==`Description` && displayed==`true`].value | []',
            # join the results from this
            'description': '@.attribute[?type==`Description` && displayed==`true`].value',
            'threat_actor_types': '@.attribute[?type==`Actor Type`].value',  # no idea
            'spec_version': '2.1',
            'type': 'threat-actor',
        }

        if isinstance(tc_data, dict):
            tc_data = [tc_data]

        for stix_data in self._map(tc_data, mapper):
            yield ThreatActor(**stix_data)
