from typing import Union
import jmespath

class StixModel:
    """STIX base model object."""

    def __init__(self):
        """Initialize Class properties."""

    def produce(self, tc_data: Union[list, dict]):
        type_mapping = {
        }
        # type_mapping = {
        #     'as object': AS(),
        #     'domain name object': DomainName(),
        #     'email address object': EmailAddress(),
        #     'email message object': EmailMessage(),
        #     'ipv4 address object': Ipv4(),
        #     'ipv6 address object': Ipv6(),
        #     'url object': Url(),
        #     'windows registry key object': RegistryKey(),
        #
        # }
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        stix_data = []
        for data in tc_data:
            type = data.get('type')
            handler = type_mapping.get(type.lower())
            stix_data.append(handler.produce(data))

        flattened_stix_data = [y for x in stix_data for y in x]

        for stix_data in flattened_stix_data:
            yield stix_data

    def consume(self, stix_data: Union[list, dict]):
        raise NotImplementedError

    @staticmethod
    def _map(data: dict, mapping: dict) -> dict:
        mapped_obj = {}

        for key, value in mapping.items():
            if not value.startswith('@'):
                mapped_obj[key] = value
            else:
                mapped_obj[key] = jmespath.search(f"{value}", jmespath.search('@', data))

        return mapped_obj

