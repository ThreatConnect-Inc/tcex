"""Top-level Stix Model Class."""
# standard library
import itertools
from typing import Dict, Iterable, Union

# third-party
import jmespath
from stix2.base import _STIXBase

# first-party
from tcex.logger import Logger


class StixModel:
    """STIX base model object."""

    def __init__(self, logger: Logger):
        """Initialize Class properties."""
        self.logger = logger
        self._as_object = None
        self._ipv4 = None
        self._ipv6 = None
        self._registry_key = None
        self._url = None
        self._domain_name = None
        self._email_address = None
        self._indicator = None
        self._relationship = None
        self._indicator_type_details = None

        self._visitors = []

    def _construct_summary(self, data, indicator_type):
        if 'summary' in data.keys():
            return data.get('summary')

        details = self.indicator_type_details.get(indicator_type)

        summary = []
        for field in details.get('fields', []):
            if field in data:
                summary.append(data.get(field))
            else:
                summary.append('')

        return ' : '.join(summary)

    @property
    def indicator_type_details(self):
        """Details for individual ThreatConnect indicator types."""
        if not self._indicator_type_details:
            # first-party
            from tcex.stix.indicator.stix_pattern_helpers import (
                address_stix_pattern_producer,
                asn_stix_pattern_producer,
                cidr_stix_pattern_producer,
                email_address_stix_pattern_producer,
                file_stix_pattern_producer,
                host_stix_pattern_producer,
                registery_key_stix_pattern_producer,
                url_stix_pattern_producer,
            )

            self._indicator_type_details = {
                'host': {
                    'lambda': host_stix_pattern_producer,
                    'api_branch': 'host',
                    'fields': ['text'],
                },
                'url': {
                    'lambda': url_stix_pattern_producer,
                    'api_branch': 'url',
                    'fields': ['text'],
                },
                'emailaddress': {
                    'lambda': email_address_stix_pattern_producer,
                    'api_branch': 'emailaddress',
                    'fields': ['addresses'],
                },
                'asn': {
                    'lambda': asn_stix_pattern_producer,
                    'api_branch': 'asns',
                    'fields': ['as_number'],
                },
                'address': {
                    'lambda': address_stix_pattern_producer,
                    'api_branch': 'address',
                    'fields': ['ip'],
                },
                'cidr': {
                    'lambda': cidr_stix_pattern_producer,
                    'api_branch': 'cidr',
                    'fields': ['ip'],
                },
                'file': {
                    'lambda': file_stix_pattern_producer,
                    'api_branch': 'file',
                    'fields': ['md5', 'sha1', 'sha256'],
                },
                'registry key': {
                    'lambda': registery_key_stix_pattern_producer,
                    'api_branch': 'registryKey',
                    'fields': ['Key Name', 'Value Name', 'Value Type'],
                },
            }
        return self._indicator_type_details

    @property
    def as_object(self):
        """ASN Parser."""
        if not self._as_object:
            from .observables.autonomous_system import StixASObject

            self._as_object = StixASObject(self.logger)
        return self._as_object

    @property
    def ipv4(self):
        """IPv4 Parser."""
        if not self._ipv4:
            from .observables.ip_addr import StixIPv4Object

            self._ipv4 = StixIPv4Object(self.logger)
        return self._ipv4

    @property
    def ipv6(self):
        """IPv6 Parser."""
        if not self._ipv6:
            from .observables.ip_addr import StixIPv6Object

            self._ipv6 = StixIPv6Object(self.logger)
        return self._ipv6

    @property
    def registry_key(self):
        """Registry Key Parser."""
        if not self._registry_key:
            from .observables.registry_key import StixRegistryKeyObject

            self._registry_key = StixRegistryKeyObject(self.logger)
        return self._registry_key

    @property
    def url(self):
        """URL Parser."""
        if not self._url:
            from .observables.url import StixURLObject

            self._url = StixURLObject(self.logger)
        return self._url

    @property
    def email_address(self):
        """Email Address Parser."""
        if not self._email_address:
            from .observables.email_address import StixEmailAddressObject

            self._email_address = StixEmailAddressObject(self.logger)
        return self._email_address

    @property
    def domain_name(self):
        """Domain Name Parser."""
        if not self._domain_name:
            from .observables.domain_name import StixDomainNameObject

            self._domain_name = StixDomainNameObject(self.logger)
        return self._domain_name

    @property
    def indicator(self):
        """Return Indicator Parser."""
        if not self._indicator:
            from .indicator.indicator import StixIndicator

            self._indicator = StixIndicator(self.logger)
        return self._indicator

    @property
    def relationship(self):
        """Relationship Parser."""
        if not self._relationship:
            from .relationship.relationship import Relationship

            self._relationship = Relationship()
        return self._relationship

    def produce(
        self, tc_data: Union[list, dict], type_mapping: Dict = None, **kwargs
    ):  # pylint: disable=unused-argument
        """Convert ThreatConnect data (in parsed JSON format) into STIX objects.

        Args:
            tc_data: one or more ThreatConnect object dictionaries
            type_mapping: mapping of TC type to a StixModel object that can produce() it.

        Yields:
            STIX objects
        """

        type_mapping = type_mapping or {}

        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for data in tc_data:
            for indicator_type, normalized_data in self._normalize_tc_objects(data):
                if indicator_type in type_mapping:
                    yield from type_mapping.get(indicator_type).produce(
                        normalized_data, indicator_type=indicator_type
                    )
                else:
                    yield from self.relationship.produce(normalized_data)
                    yield from self.indicator.produce(
                        normalized_data, indicator_type=indicator_type
                    )

    def _normalize_tc_objects(self, tc_data):
        indicator_type = None
        api_branch = 'indicator'
        data = tc_data.get('data', tc_data)
        for key, values in self.indicator_type_details.items():
            if values.get('api_branch').upper() in [s.upper() for s in data.keys()] or values.get(
                'type', ''
            ).upper() in [s.upper() for s in data.keys()]:
                api_branch = values.get('api_branch')
                indicator_type = key
                break

        if indicator_type is None:
            for key, values in self.indicator_type_details.items():
                for field in values.get('fields'):
                    if field.lower() in map(str.lower, data.keys()):
                        indicator_type = key
                        break
                if indicator_type:
                    break

        tc_data = data.get(api_branch, data)

        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for data in tc_data:
            _type = indicator_type or data.get('type').lower()
            self.logger.log.error(f'_type: {_type}')
            data['summary'] = self._construct_summary(data, _type)
            for field in self.indicator_type_details.get(_type).get('fields'):
                data.pop(field, '')
            yield _type, data

    # pylint: disable=unused-argument
    def consume(self, stix_data: Union[list, dict], type_mapping: Dict = None, **kwargs):
        """Convert stix_data (in parsed JSON format) into ThreatConnect objects.

        Args:
            stix_data: one or more stix_data dictionaries
            type_mapping: mapping of stix type to a StixModel object that can consume() it.

        Yields:
            ThreatConnect objects
        """
        type_mapping = {
            'autonomous-system': self.as_object,
            'domain-name': self.domain_name,
            'email-addr': self.email_address,
            'ipv4-addr': self.ipv4,
            'ipv6-addr': self.ipv6,
            'windows-registry-key': self.registry_key,
            'url': self.url,
            'indicator': self.indicator,
        }.update(type_mapping or {})

        visitor_mapping = {'relationship': self.relationship}

        if not isinstance(stix_data, list):
            stix_data = [stix_data]

        tc_data = []
        for data in stix_data:
            # Handle a bundle OR just one or more stix objects.
            stix_objects = data.get('objects') if data.get('type') == 'bundle' else data

            for stix_object in stix_objects:
                _type = stix_object.get('type').lower()
                if _type in visitor_mapping:
                    for visitor in visitor_mapping.get(_type).consume(stix_object):
                        self.register_visitor(visitor)
                else:
                    if _type in type_mapping:
                        # sub-parsers return generators, so chain them all together to flatten.
                        tc_data = itertools.chain(
                            tc_data, type_mapping.get(_type).consume(stix_object)
                        )
                    else:
                        # TODO handle unknown stix type
                        pass

        for visitor in self._visitors:
            tc_data = visitor.visit(tc_data)

        yield from tc_data

    def register_visitor(self, visitor):
        """Register a visitor that will be passed all parsed data after consume is through."""
        self._visitors.append(visitor)

    def _map(self, data: Union[list, dict], mapping: dict):

        if isinstance(data, dict):
            data = [data]
        try:
            for d in data:
                mapped_obj = mapping.copy()
                for key, value in mapping.items():
                    if isinstance(value, list):
                        new_list = []
                        for item in value:
                            new_list.append(list(self._map(d, item))[0])

                        mapped_obj[key] = new_list
                    elif isinstance(value, dict):
                        mapped_obj[key] = list(self._map(d, mapped_obj[key]))[0]
                    else:
                        if not value.startswith('@'):
                            mapped_obj[key] = value
                        else:
                            mapped_obj[key] = jmespath.search(f'{value}', jmespath.search('@', d))
                yield mapped_obj
        except Exception:  # pylint: disable=bare-except
            self.logger.log.error(f'Could not map {data} using {mapping}')


class JMESPathStixModel(StixModel):
    """Generic implmenetation of StixModel that converts data based on jmespath statements."""

    def __init__(
        self,
        produce_map: Dict[str, str],
        produce_type: _STIXBase,
        consume_map: Dict[str, str],
        logger: Logger,
    ):
        """Instantiate a JMESPath StixModel.

        Args:
            produce_map: map of target field name to a jmespath query to pull that data from the
                tc object.
            produce_type: The class to use for the STIX object.
            consume_map: map of target field name to a jmespath query to pull data from the stix
                object.
            logger: logger
        """
        super().__init__(logger)
        self._produce_map = produce_map
        self._produce_type = produce_type
        self._consume_map = consume_map

    # pylint: disable=arguments-differ
    def produce(self, tc_data: Union[list, dict], **kwargs) -> Iterable:
        """Accept TC entities and produces STIX objects."""
        yield from (
            self._produce_type(**stix_data) for stix_data in self._map(tc_data, self._produce_map)
        )

    # pylint: disable=arguments-differ
    def consume(self, stix_data: Union[list, dict], **kwargs):
        """Accept STIX objects and produces TC Entities."""
        yield from self._map(stix_data, self._consume_map)
