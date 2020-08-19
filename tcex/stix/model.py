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

        self._visitors = []

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

        type_mapping = {
            'indicator': self.indicator,
            # 'asn': self.as_object,
            # 'host': self.domain_name,
            # 'emailaddress': self.email_address,
            # 'address': self.ipv4,
            # 'registry key': self.registry_key,
            # 'url': self.url

        }
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for data in tc_data:
            _type = data.get('type').lower()
            handler = type_mapping.get(_type.lower(), _type.lower())
            yield from handler.produce(data)

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
            stix_objects = \
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

    @staticmethod
    def _add_association(target, source):
        target.setdefault('associations', []).append(
            {
                'name': source.get('summary'),
                'type': source.get('type'),
            }
        )
        source.setdefault('associations', []).append(
            {
                'name': target.get('summary'),
                'type': target.get('type'),
            }
        )

    @staticmethod
    def _partition(l, p):
        return reduce(lambda x, y: (x[0] + [y], x[1]) if p(y) else (x[0], x[1] + [y]), l, ([], []))


