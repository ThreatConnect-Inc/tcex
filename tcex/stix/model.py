"""Top-level Stix Model Class."""
# standard library
import itertools
from typing import Union
from functools import reduce
import jmespath


class StixModel:
    """STIX base model object."""

    def __init__(self):
        """Initialize Class properties."""
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
        print(data)
        for field in details.get('fields'):
            print(data.get(field))
            summary.append(data.get(field))

        return ' : '.join(summary)

    @property
    def indicator_type_details(self):
        if not self._indicator_type_details:
            from .indicator.indicator import Indicator

            self._indicator_type_details = {
                'host': {
                    'lambda': lambda data: f"[domain-name:value = '{data.get('summary')}']",
                    'api_branch': 'hosts',
                    'fields': ['text']
                },
                'url': {
                    'lambda': lambda data: f"[url:value = '{data.get('summary')}']",
                    'api_branch': 'urls',
                    'fields': ['text']
                },
                'emailaddress': {
                    'lambda': lambda data: f"[email-addr:value = '{data.get('summary')}']",
                    'api_branch': 'emailaddresses',
                    'fields': ['addresses']
                },
                'asn': {
                    'lambda': lambda data: f"[autonomous-system:name = '{data.get('summary')}']",
                    'api_branch': 'asns',
                    'fields': ['as_number']
                },
                'address': {
                    'lambda': Indicator._address_producer_helper,
                    'api_branch': 'address',
                    'fields': ['ip']
                },
                'cidr': {
                    'lambda': Indicator._cidr_producer_helper,
                    'api_branch': 'address',
                    'fields': ['ip']
                },
                'file': {
                    'lambda': Indicator._file_producer_helper,
                    'api_branch': 'files',
                    'fields': ['md5', 'sha1', 'sha256']
                },
                'registry key': {
                    'lambda': Indicator._file_producer_helper,
                    'api_branch': 'registryKeys',
                    'fields': ['key name', 'value name', 'value type']
                },
            }
        return self._indicator_type_details

    @property
    def as_object(self):
        if not self._as_object:
            from .observables.autonomous_system import StixASObject

            self._as_object = StixASObject()
        return self._as_object

    @property
    def ipv4(self):
        if not self._ipv4:
            from .observables.ipv4 import StixIPv4Object

            self._ipv4 = StixIPv4Object()
        return self._ipv4

    @property
    def ipv6(self):
        if not self._ipv6:
            from .observables.ipv6 import StixIPv6Object

            self._ipv6 = StixIPv6Object()
        return self._ipv6

    @property
    def registry_key(self):
        if not self._registry_key:
            from .observables.registry_key import WindowsRegistryKey

            self._registry_key = WindowsRegistryKey()
        return self._registry_key

    @property
    def url(self):
        if not self._url:
            from .observables.url import StixURLObject

            self._url = StixURLObject()
        return self._url

    @property
    def email_address(self):
        if not self._email_address:
            from .observables.email_address import StixEmailAddressObject

            self._email_address = StixEmailAddressObject()
        return self._email_address

    @property
    def domain_name(self):
        if not self._domain_name:
            from .observables.domain_name import StixDomainNameObject

            self._domain_name = StixDomainNameObject()
        return self._domain_name

    @property
    def indicator(self):
        if not self._indicator:
            from .indicator.indicator import Indicator

            self._indicator = Indicator()
        return self._indicator

    @property
    def relationship(self):
        if not self._relationship:
            from .relationship.relationship import Relationship
            self._relationship = Relationship(self)
        return self._relationship

    def produce(self, tc_data: Union[list, dict]):
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for data in tc_data:
            for indicator_type, normalized_data in self.normalize_tc_objects(data):
                yield from self.relationship.produce(normalized_data)
                yield from self.indicator.produce(normalized_data, indicator_type=indicator_type)

    def normalize_tc_objects(self, tc_data):
        indicator_type = None
        api_branch = 'indicator'
        data = tc_data.get('data', tc_data)
        for key, values in self.indicator_type_details.items():
            if values.get('api_branch') in data.keys():
                api_branch = values.get('api_branch')
                indicator_type = key
                break
        tc_data = data.get(api_branch)

        for data in tc_data:
            _type = indicator_type or data.get('type').lower()
            data['summary'] = self._construct_summary(data, indicator_type)
            for field in self.indicator_type_details.get(_type).get('fields'):
                data.pop(field, '')
            yield indicator_type, data

    def consume(self, stix_data: Union[list, dict]):
        type_mapping = {
            'autonomous-system': self.as_object,
            'domain-name': self.domain_name,
            'email-addr': self.email_address,
            'ipv4-addr': self.ipv4,
            'ipv6-addr': self.ipv6,
            'windows-registry-key': self.registry_key,
            'url': self.url,
            'indicator': self.indicator,
        }

        visitor_mapping = {
            'relationship': self.relationship
        }

        if not isinstance(stix_data, list):
            stix_data = [stix_data]

        tc_data = []
        for stix_data in stix_data:
            # Handle a bundle OR just one or more stix objects.
            stix_objects = stix_data
            if stix_data.get('type') == 'bundle':
                stix_objects = stix_data.get('objects')
                stix_data.get('objects') if stix_data.get('type') == 'bundle' else stix_data

            for stix_object in stix_objects:
                _type = stix_object.get('type').lower()
                if _type in visitor_mapping:
                    visitor_mapping.get(_type).consume(stix_object)
                else:
                    if _type in type_mapping:
                        # sub-parsers return generators, so chain them all together to flatten.
                        tc_data = itertools.chain(
                            tc_data,
                            type_mapping.get(_type).consume(stix_object))
                    else:
                        # TODO handle unknown stix type
                        pass

        for visitor in self._visitors:
            tc_data = visitor.visit(tc_data)

        yield from tc_data

    def register_visitor(self, visitor):
        self._visitors.append(visitor)

    def _map(self, data: Union[list, dict], mapping: dict):

        if isinstance(data, dict):
            data = [data]

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

