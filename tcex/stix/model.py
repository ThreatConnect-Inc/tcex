"""Top-level Stix Model Class."""
# standard library
import copy
import itertools
from operator import methodcaller
from typing import Dict, Iterable, Union

# third-party
import jmespath
from stix2.base import _STIXBase

# first-party
from tcex.batch import Batch
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
        self.default_map = {
            'dateAdded': '@.created',
            'lastModified': '@.modified',
            'tag': '@.labels',
            'securityLabel': '@.object_marking_refs',
            'attribute': [
                {'type': 'STIX Title', 'value': '@.name'},
                {'type': 'Description', 'value': '@.description'},
                {'type': 'STIX Indicator Type', 'value': '@.indicator_types'},
                {'type': 'External Date Created', 'value': '@.valid_from'},
                {'type': 'External Date Expires', 'value': '@.valid_until'},
                {'type': 'Source', 'value': 'WILL BE REPLACED IN THE CONSUME METHOD'},
            ],
        }

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
    def security_label_map(self):
        """Map of TLP labels to STIX marking-definitions."""
        return {
            'tlp:white': 'marking-definition--613f2e26-407d-48c7-9eca-b8e91df99dc9',
            'tlp:green': 'marking-definition--34098fce-860f-48ae-8e50-ebd3cc5e41da',
            'tlp:amber': 'marking-definition--f88d31f6-486f-44da-b317-01333bde0b82',
            'tlp:red': 'marking-definition--5e57c739-391a-4eb3-b6be-7d15ca92d5ed',
        }

    @property
    def x_threat_rating_map(self):
        """Map of Threat Rating Numbers to Labels."""
        return {
            '0': 'Threat Rating: Unknown',
            '1': 'Threat Rating: Suspicious',
            '2': 'Threat Rating: Low',
            '3': 'Threat Rating: Moderate',
            '4': 'Threat Rating: High',
            '5': 'Threat Rating: Very High',
        }

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
            if _type not in self.indicator_type_details:
                self.logger.log.info(f'unable to convert indicator type {_type} to stix object')
                continue
            data['summary'] = self._construct_summary(data, _type)
            for field in self.indicator_type_details.get(_type).get('fields'):
                data.pop(field, '')
            yield _type, data

    # pylint: disable=unused-argument,no-self-use
    def as_object_mapping(self, stix_data):
        """Produce ThreatConnect ASN mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        return {
            'type': 'ASN',
            'summary': '@.number',
            'confidence': '@.confidence',
        }

    # pylint: disable=unused-argument,no-self-use
    def domain_name_mapping(self, stix_data):
        """Produce ThreatConnect Host mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        return {
            'type': 'Host',
            'summary': '@.value',
            'confidence': '@.confidence',
        }

    # pylint: disable=unused-argument,no-self-use
    def email_address_mapping(self, stix_data):
        """Produce ThreatConnect EmailAddress mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        return {
            'type': 'EmailAddress',
            'summary': '@.value',
            'confidence': '@.confidence',
        }

    # pylint: disable=unused-argument,no-self-use
    def _ip_addr_mapping(self, stix_data, full_block_size):
        """Produce ThreatConnect Address/CIDR mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        cidr_parts = stix_data.get('value', '').split('/')
        cidr_suffix = cidr_parts[1] if len(cidr_parts) > 1 else str(full_block_size)
        if cidr_suffix == str(full_block_size):
            return {
                'type': 'Address',
                'summary': '@.value',
                'confidence': '@.confidence',
            }
        return {
            'confidence': '@.confidence',
            'type': 'CIDR',
            'summary': '@.value',
        }

    # pylint: disable=unused-argument,no-self-use
    def ipv6_mapping(self, stix_data):
        """Produce ThreatConnect Address/CIDR mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        return self._ip_addr_mapping(stix_data, 128)

    # pylint: disable=unused-argument,no-self-use
    def ipv4_mapping(self, stix_data):
        """Produce ThreatConnect Address/CIDR mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        return self._ip_addr_mapping(stix_data, 32)

    # pylint: disable=unused-argument,no-self-use
    def url_mapping(self, stix_data):
        """Produce ThreatConnect URL mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        return {'type': 'URL', 'summary': '@.value', 'confidence': '@.confidence'}

    # pylint: disable=unused-argument,no-self-use
    def registry_key_mapping(self, stix_data):
        """Produce ThreatConnect Registry Key mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A indicator mappings.
        """

        mapper = {
            'type': 'Registry Key',
            'Key Name': '@.key',
            'confidence': '@.confidence',
        }
        if not stix_data.get('values'):
            return mapper

        for i in range(len(stix_data.get('values'))):
            mapper['Value Name'] = f'@.values[{i}].name'
            mapper['Value Type'] = f'@.values[{i}].data_type'
            mapper.setdefault('attribute', []).append(
                {'type': 'Value Data', 'value': f'@.values[{i}].data'}
            )
        return mapper

    def consume(
        self,
        stix_data: dict,
        collection_id,
        collection_name,
        collection_path,
        custom_type_mapping: dict = None,
    ):
        """Convert stix_data (in parsed JSON format) into ThreatConnect objects.

        Args:
            stix_data: one or more stix_data dictionaries
            collection_path: the url path to the collection
            collection_name: the collection name
            collection_id: the collection id
            custom_type_mapping: stix type to a mapping function which takes stix_data as a param.

        Yields:
            ThreatConnect objects
        """
        type_mapping = {
            'email-addr': self.email_address_mapping,
            'autonomous-system': self.as_object_mapping,
            'domain-name': self.domain_name_mapping,
            'ipv4-addr': self.ipv4_mapping,
            'ipv6-addr': self.ipv6_mapping,
            'windows-registry-key': self.registry_key_mapping,
            'url': self.url_mapping,
        }
        type_mapping.update(custom_type_mapping or {})
        visitor_mapping = {'relationship': self.relationship}

        tc_data = []
        for data in stix_data.get('objects', []):
            object_id = data.get('id')
            xid = Batch.generate_xid(object_id)
            safe_default_map = copy.deepcopy(self.default_map)
            source_value = [f'Object ID: {object_id}']
            if collection_id:
                source_value.append(f'Collection ID: {collection_id}')
                xid = Batch.generate_xid([object_id, collection_id])
            if collection_name:
                source_value.append(f'Collection Name: {collection_name}')
            if collection_path:
                source_value.append(f'Collection Path: {collection_path}')
                if not collection_path.endswith('/'):
                    collection_path += '/'
                source_value.append(f'Object Path: {collection_path}objects/{object_id}/')
            for attribute in safe_default_map.get('attribute', []):
                if attribute.get('type') == 'Source':
                    attribute['value'] = '\n'.join(source_value)
                    attribute['displayed'] = True
                    break
            _type = data.get('type').lower()
            mapping_method = visitor_mapping.get(_type)
            if mapping_method:
                # for visitor in mapping_method.consume(data):
                #     self.register_visitor(visitor)
                continue
            mapping_method = type_mapping.get(_type)
            if _type == 'indicator':
                if stix_data.get('pattern_type', 'stix') != 'stix':
                    continue
                for map_ in self.indicator.consume_mappings(data, collection_id):
                    if not map_:
                        continue
                    map_.update(safe_default_map)
                    tc_data = itertools.chain(tc_data, self._map(data, map_))
            elif mapping_method:
                safe_default_map['xid'] = xid
                map_ = self.smart_update(safe_default_map, mapping_method(data))
                tc_data = itertools.chain(tc_data, self._map(data, map_))
            # else:
            #     self.default_map['xid'] = xid
            #     tc_data = itertools.chain(tc_data, self._map(data, self.default_map))
            #     continue

        for visitor in self._visitors:
            tc_data = visitor.visit(tc_data)

        yield from tc_data

    @staticmethod
    def smart_update(list_one, list_two):
        """Update one dict with the other but joins arrays."""
        updated_dict = {}
        dict_items = map(methodcaller('items'), (list_one, list_two))
        for k, v in itertools.chain.from_iterable(dict_items):
            if isinstance(v, list) and isinstance(updated_dict.get(k), list):
                updated_dict[k].extend(v)
            else:
                updated_dict[k] = v
        return updated_dict

    def register_visitor(self, visitor):
        """Register a visitor that will be passed all parsed data after consume is through."""
        self._visitors.append(visitor)

    def _map(self, data: Union[list, dict], mapping: dict):
        """Produce a dict with the appropriate values given data and a mapping.

        Args:
            data: The data to be referenced in the mappings
            mapping: The default values and jmspaths to the appropiate values in data.

        Returns:
            A new dict produced by the mappings and data field.
        """
        if isinstance(data, dict):
            data = [data]
        for d in data:
            mapped_obj = mapping.copy()
            for key, value in mapping.items():
                if isinstance(value, str) and not value.startswith('@'):
                    mapped_obj[key] = value
                    continue
                if isinstance(value, (dict, list)):
                    value = copy.deepcopy(value)

                if key in ['securityLabel', 'tag', 'attribute']:
                    mapped_value = self._custom_stix_mapping(d, key, value)
                    if mapped_value:
                        mapped_obj[key] = mapped_value
                    else:
                        del mapped_obj[key]
                else:
                    if isinstance(value, list):
                        new_list = []
                        for item in value:
                            new_list.append(list(self._map(d, item))[0])

                        mapped_obj[key] = new_list
                        continue
                    if isinstance(value, dict):
                        mapped_obj[key] = list(self._map(d, mapped_obj[key]))[0]
                        continue

                    resolved_value = jmespath.search(f'{value}', jmespath.search('@', d)) or []
                    if resolved_value:
                        mapped_obj[key] = resolved_value
                    else:
                        del mapped_obj[key]
            yield mapped_obj

    @staticmethod
    def _remove_milliseconds(time):
        time = time.split('.')
        milliseconds = ''
        if len(time) > 1:
            milliseconds = time.pop()
        new_time = ''.join(time)
        if milliseconds.lower().endswith('z'):
            return f'{new_time}Z'
        return new_time

    def _custom_stix_mapping(self, data, key, value):
        if key == 'securityLabel':
            resolved_values = jmespath.search(f'{value}', jmespath.search('@', data)) or []
            object_marking_refs = []
            for resolved_value in resolved_values:
                resolved_value = resolved_value.lower()
                if resolved_value in self.security_label_map.values():
                    security_label = list(self.security_label_map.keys())[
                        list(self.security_label_map.values()).index(resolved_value)
                    ]
                    object_marking_refs.append({'name': security_label.upper()})
            return object_marking_refs
        if key == 'tag':
            resolved_values = jmespath.search(f'{value}', jmespath.search('@', data)) or []
            tags = []
            for resolved_value in resolved_values:
                tags.append({'name': resolved_value})
            return tags
        if key == 'attribute':
            attributes = []
            for attribute in value:
                attribute_value = attribute.get('value')
                if isinstance(attribute_value, str):
                    if attribute.get('value', '').startswith('@'):
                        attribute_value = (
                            jmespath.search(f'{attribute_value}', jmespath.search('@', data)) or []
                        )
                        if isinstance(attribute_value, list):
                            attribute_value = '\n'.join(attribute_value)
                        if attribute.get('value') in ['@.valid_from', '@.valid_until']:
                            attribute_value = self._remove_milliseconds(attribute_value)
                if not attribute_value:
                    continue
                attribute['value'] = attribute_value
                attributes.append(attribute)
            return attributes
        return None

        # return mapped_obj
        #     if not object_marking_refs:
        #         del mapped_obj[key]
        #     else:
        #         mapped_obj[key] = []
        #     for object_marking_ref in object_marking_refs:
        #         object_marking_ref = object_marking_ref.lower()
        #         if object_marking_ref in self.security_label_map.values():
        #             security_label = list(self.security_label_map.keys())[
        #                 list(self.security_label_map.values()).index(object_marking_ref)]
        #             mapped_obj[key].append({'name': security_label.upper()})
        # elif key == 'tag':
        #     tags = jmespath.search(f'{value}', jmespath.search('@', d)) or []
        #     if not tags:
        #         del mapped_obj[key]
        #     else:
        #         mapped_obj = []
        #     for tag in tags:
        #         mapped_obj[key].append({'name': tag})
        # else:
        #     if key == 'attribute':
        #         attributes = jmespath.search(f'{value}', jmespath.search('@', d)) or []
        #         if not attributes:
        #             del mapped_obj[key]
        #     mapped_obj[key] = jmespath.search(f'{value}', jmespath.search('@', d))


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

    # pylint: disable=arguments-differ, unused-argument
    def consume(self, stix_data: Union[list, dict], **kwargs):
        """Accept STIX objects and produces TC Entities."""
        yield from self._map(stix_data, self._consume_map)
