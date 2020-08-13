"""Top-level Stix Model Class."""
# standard library
from .registry_key import WindowsRegistryKey
from .url import URL
from .ipv4 import IPv4Address
from .ipv6 import IPv6Address
from .cyber_observables import *
# third-party
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

    @property
    def as_object(self):
        if not self._as_object:
            self._as_object = StixASObject()
        return self._as_object

    @property
    def ipv4(self):
        if not self._ipv4:
            self._ipv4 = IPv4Address()
        return self._ipv4

    @property
    def ipv6(self):
        if not self._ipv6:
            self._ipv6 = IPv6Address()
        return self._ipv6

    @property
    def registry_key(self):
        if not self._registry_key:
            self._registry_key = WindowsRegistryKey()
        return self._registry_key

    @property
    def url(self):
        if not self._url:
            self._url = URL()
        return self._url

    @property
    def email_address(self):
        if not self._email_address:
            self._email_address = StixEmailAddressObject()
        return self._email_address

    @property
    def domain_name(self):
        if not self._domain_name:
            self._domain_name = StixDomainNameObject()
        return self._domain_name

    def produce(self, tc_data: Union[list, dict]):

        type_mapping = {
            'asn': self.as_object,
            'host': self.domain_name,
            'emailaddress': self.email_address,
            'address': self.ipv4,
            'registry key': self.registry_key,
            'url': self.url

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
            'url': self.url
        }

        if not isinstance(stix_data, list):
            stix_data = [stix_data]

        for data in stix_data:
            type = data.get('type').lower()
            handler = type_mapping.get(type.lower(), type.lower())
            yield from handler.produce(data)

    @staticmethod
    def _map(data: Union[list, dict], mapping: dict):

        if isinstance(data, dict):
            data = [data]

        for d in data:
            mapped_obj = mapping.copy()
            for key, value in mapping.items():
                if isinstance(value, list):
                    new_list = []
                    for item in value:
                        new_list.append(list(StixModel._map(d, item))[0])

                    mapped_obj[key] = new_list
                elif isinstance(value, dict):
                    mapped_obj[key] = list(StixModel._map(d, mapped_obj[key]))[0]
                else:
                    if not value.startswith('@'):
                        mapped_obj[key] = value
                    else:
                        mapped_obj[key] = jmespath.search(f'{value}', jmespath.search('@', d))
            yield mapped_obj
