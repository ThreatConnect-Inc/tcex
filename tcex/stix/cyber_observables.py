"""Implement parsers for STIX 2.0 JSON Cyber-Domain Observable objects."""
# standard library
from typing import Iterable, Union

# third-party
from stix2 import AutonomousSystem, DomainName, EmailAddress

from .threat_actor import StixModel  # pylint: disable=relative-beyond-top-level


class StixASObject(StixModel):
    """Parser for STIX AS Object.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070683
    """

    def produce(self, tc_data: Union[list, dict]) -> Iterable[AutonomousSystem]:
        """Produce STIX 2.0 JSON object from TC API response."""
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'AS Number'

        for data in list(tc_data):
            yield AutonomousSystem(
                **self._map(
                    data,
                    {
                        'type': 'autonomous-system',
                        'spec_version': '2.1',
                        'id': '@.id',
                        'number': f'@."{indicator_field}"',
                    },
                )
            )

    def consume(self, stix_data: Union[list, dict]):
        """Produce a ThreatConnect object from a STIX 2.0 JSON object."""
        return self._map(stix_data, {'AS Number': '@.number'})


class StixDomainNameObject(StixModel):
    """Parser for STIX Domain Name Object.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070687
    """

    def produce(self, tc_data: Union[list, dict]) -> Iterable[DomainName]:
        """Produce STIX 2.0 JSON object from TC API response."""
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'hostName'

        for data in list(tc_data):
            yield DomainName(
                **self._map(
                    data,
                    {
                        'type': 'domain-name',
                        'spec_version': '2.1',
                        'id': '@.id',
                        'value': f'@."{indicator_field}"',
                    },
                )
            )

    def consume(self, stix_data: Union[list, dict]):
        """Produce a ThreatConnect object from a STIX 2.0 JSON object."""
        return self._map(stix_data, {'hostName': '@.value'})


class StixEmailAddressObject(StixModel):
    """Parser for STIX Email Address Object.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070690
    """

    def produce(self, tc_data: Union[list, dict]) -> Iterable[EmailAddress]:
        """Produce STIX 2.0 JSON object from TC API response."""
        if isinstance(tc_data, list) and len(tc_data) > 0 and 'summary' in tc_data[0]:
            indicator_field = 'summary'
        else:
            indicator_field = 'address'

        for data in list(tc_data):
            yield EmailAddress(
                **self._map(
                    data,
                    {
                        'type': 'email-addr',
                        'spec_version': '2.1',
                        'id': '@.id',
                        'value': f'@."{indicator_field}"',
                    },
                )
            )

    def consume(self, stix_data: Union[list, dict]):
        """Produce a ThreatConnect object from a STIX 2.0 JSON object."""
        return self._map(stix_data, {'hostName': '@.value'})
