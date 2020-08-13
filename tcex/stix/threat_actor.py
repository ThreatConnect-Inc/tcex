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


class StixThreatActor(StixModel):
    """STIX Threat Actor object."""

    @property
    def produce_map(self):
        # mapping of STIX fields to TC jmespath expressions
        return {
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
            'type': 'threat-actor'
        }

    def consume(self, stix_data: Union[list, dict]):
        pass

    def produce(self, tc_data: Union[list, dict]):
        """Produce STIX 2.0 JSON object from TC API response.

        .. code:: json

            {
              "id": 130292,
              "name": "kpot",
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
        map = {
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
            'type': 'threat-actor'
        }

        tc_data = list(tc_data)

        for stix_data in self._map(tc_data, map):
            return ThreatActor(**stix_data)

        # return ThreatActor(
        #     id='threat-actor--9a8a0d25-7636-429b-a99e-b2a73cd0f11f',
        #     created='2015-05-07T14:22:14.760Z',
        #     modified='2015-05-07T14:22:14.760Z',
        #     name='Adversary Bravo',
        #     description='Adversary Bravo is known to use phishing attacks to deliver remote access malware to the targets.',
        #     threat_actor_types=['spy', 'criminal'],
        #     spec_version='2.1',
        #     type='threat-actor',
        # )

# identity = Identity(
#     id="identity--1621d4d4-b67d-41e3-9670-f01faf20d111",
#     created="2015-05-10T16:27:17.760Z",
#     modified="2015-05-10T16:27:17.760Z",
#     name="Adversary Bravo",
#     description="Adversary Bravo is a threat actor that utilizes phishing attacks.",
#     identity_class="unknown",
#     spec_version="2.1",
#     type="identity",
# )

# init_comp = KillChainPhase(
#     kill_chain_name="mandiant-attack-lifecycle-model", phase_name="initial-compromise"
# )
#
# malware = Malware(
#     id="malware--d1c612bc-146f-4b65-b7b0-9a54a14150a4",
#     created="2015-04-23T11:12:34.760Z",
#     modified="2015-04-23T11:12:34.760Z",
#     name="Poison Ivy Variant d1c6",
#     malware_types=["remote-access-trojan"],
#     kill_chain_phases=[init_comp],
#     spec_version="2.1",
#     type="malware",
#     is_family="false",
# )
#
# ref = ExternalReference(
#     source_name="capec",
#     description="phishing",
#     url="https://capec.mitre.org/data/definitions/98.html",
#     external_id="CAPEC-98",
# )
#
# attack_pattern = AttackPattern(
#     id="attack-pattern--8ac90ff3-ecf8-4835-95b8-6aea6a623df5",
#     created="2015-05-07T14:22:14.760Z",
#     modified="2015-05-07T14:22:14.760Z",
#     name="Phishing",
#     description="Spear phishing used as a delivery mechanism for malware.",
#     kill_chain_phases=[init_comp],
#     external_references=[ref],
#     spec_version="2.1",
#     type="attack-pattern",
# )
#
# relationship1 = Relationship(threat_actor, 'uses', malware)
# relationship2 = Relationship(threat_actor, 'uses', attack_pattern)
# relationship3 = Relationship(threat_actor, 'attributed-to', identity)
#
# bundle = Bundle(
#     objects=[
#         threat_actor,
#         malware,
#         attack_pattern,
#         identity,
#         relationship1,
#         relationship2,
#         relationship3,
#     ]
# )
#
#         """Produce STIX 2.0 JSON object from TC API response.
#
#         .. code:: json
#
#             {
#               "indicator": [
#                 {
#                   "id": 4716778,
#                   "ownerName": "TCI",
#                   "type": "Address",
#                   "dateAdded": "2020-07-30T13:40:24Z",
#                   "lastModified": "2020-07-30T13:40:24Z",
#                   "rating": 3.00,
#                   "confidence": 100,
#                   "threatAssessRating": 3.0,
#                   "threatAssessConfidence": 100.0,
#                   "threatAssessScore": 503,
#                   "webLink": "https://int-tc-01.tci.ninja/auth/indicators/details/address.xhtml?address=51.178.15.11&owner=TCI",
#                   "summary": "51.178.15.11",
#                   "attribute": [
#                     {
#                       "id": 12592341,
#                       "type": "External Date Expires",
#                       "value": "2022-02-28T00:00:00Z",
#                       "dateAdded": "2020-07-30T13:40:24Z",
#                       "lastModified": "2020-07-30T13:40:24Z",
#                       "displayed": false
#                     }
#                   ],
#                   "tag": [
#                     {
#                       "name": "MATCHING CONDITION: Equal",
#                       "webLink": "https://int-tc-01.tci.ninja/auth/tags/tag.xhtml?tag=MATCHING+CONDITION%3A+Equal&owner=TCI"
#                     },
#                     {
#                       "name": "BAE CONTEXT: Unclassified",
#                       "webLink": "https://int-tc-01.tci.ninja/auth/tags/tag.xhtml?tag=BAE+CONTEXT%3A+Unclassified&owner=TCI"
#                     },
#                     {
#                       "name": "BAE:Confidence:5",
#                       "webLink": "https://int-tc-01.tci.ninja/auth/tags/tag.xhtml?tag=BAE%3AConfidence%3A5&owner=TCI"
#                     }
#                   ],
#                   "observationCount": 0,
#                   "falsePositiveCount": 0,
#                   "privateFlag": false,
#                   "active": true,
#                   "activeLocked": false
#                 },
#                 {
#                   "id": 4716777,
#                   "ownerName": "TCI",
#                   "type": "Address",
#                   "dateAdded": "2020-07-30T13:40:24Z",
#                   "lastModified": "2020-07-30T13:40:24Z",
#                   "rating": 3.00,
#                   "confidence": 100,
#                   "threatAssessRating": 3.0,
#                   "threatAssessConfidence": 100.0,
#                   "threatAssessScore": 503,
#                   "webLink": "https://int-tc-01.tci.ninja/auth/indicators/details/address.xhtml?address=158.69.30.202&owner=TCI",
#                   "summary": "158.69.30.202",
#                   "attribute": [
#                     {
#                       "id": 12592340,
#                       "type": "External Date Expires",
#                       "value": "2022-02-28T00:00:00Z",
#                       "dateAdded": "2020-07-30T13:40:24Z",
#                       "lastModified": "2020-07-30T13:40:24Z",
#                       "displayed": false
#                     }
#                   ],
#                   "tag": [
#                     {
#                       "name": "MATCHING CONDITION: Equal",
#                       "webLink": "https://int-tc-01.tci.ninja/auth/tags/tag.xhtml?tag=MATCHING+CONDITION%3A+Equal&owner=TCI"
#                     },
#                     {
#                       "name": "BAE CONTEXT: Unclassified",
#                       "webLink": "https://int-tc-01.tci.ninja/auth/tags/tag.xhtml?tag=BAE+CONTEXT%3A+Unclassified&owner=TCI"
#                     },
#                     {
#                       "name": "BAE:Confidence:5",
#                       "webLink": "https://int-tc-01.tci.ninja/auth/tags/tag.xhtml?tag=BAE%3AConfidence%3A5&owner=TCI"
#                     }
#                   ],
#                   "observationCount": 0,
#                   "falsePositiveCount": 0,
#                   "privateFlag": false,
#                   "active": true,
#                   "activeLocked": false
#                 }
#               ]
#             }
#
#
#         """
