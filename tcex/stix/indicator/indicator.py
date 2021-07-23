"""Parser for STIX Indicator Objects.

import stix2
see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070633
"""
# standard library
import itertools
import uuid
from datetime import datetime
from typing import Iterable, Union

# first-party
from tcex.batch import Batch
from tcex.stix import StixModel  # pylint: disable=cyclic-import

from .stix2_lark import Indicator, Stix2IndicatorParser


class StixIndicator(StixModel):
    """Parser for STIX Indicator Objects.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070633
    """

    def __init__(self, logger):
        """Initialize stix parser."""
        super().__init__(logger)
        self.stix_parser = Stix2IndicatorParser()

    @staticmethod
    def _add_milliseconds(time):
        new_time = f'''{time.upper().replace('Z', '')}.000'''
        if time.lower().endswith('z'):
            return f'{new_time}Z'
        return new_time

    # pylint: disable=arguments-differ
    def produce(self, tc_data: Union[list, dict], **kwargs):
        """Produce a STIX Indicator from a ThreatConnect Indicator.

        Args:
            tc_data: ThreatConnect indicator(s)

        Yields:
            A STIX Indicator.
        """
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for data in tc_data:
            _type = kwargs.get('indicator_type') or data.get('type')
            indicator_details = self.indicator_type_details.get(_type.lower())
            if not indicator_details:
                continue
            kwargs = {
                'pattern_type': 'stix',
                'lang': 'en',
                'pattern_version': '2.1',
                'type': 'indicator',
                'created': self._add_milliseconds(data.get('dateAdded')),
                'valid_from': self._add_milliseconds(data.get('dateAdded')),
                'modified': self._add_milliseconds(data.get('lastModified')),
                'name': data.get('summary'),
                'pattern': indicator_details.get('lambda')(data),
                'description': '',
                'indicator_types': ['malicious-activity'],
                'confidence': data.get('confidence', 0),
            }
            if not data.get('active', True):
                kwargs['revoked'] = True
            latest = None
            for tag in data.get('tag', []):
                kwargs.setdefault('labels', []).append(tag.get('name'))
            for security_label in data.get('securityLabel', []):
                security_label = security_label.get('name', '').strip().lower()
                if security_label in self.security_label_map:
                    kwargs.setdefault('object_marking_refs', [])
                    kwargs['object_marking_refs'].append(
                        self.security_label_map.get(security_label)
                    )
            for attribute in data.get('attribute', []):
                if attribute.get('type').lower() == 'description':
                    value = attribute.get('value')
                    last_modified = datetime.strptime(
                        attribute.get('lastModified'), '%Y-%m-%dT%H:%M:%SZ'
                    )
                    if attribute.get('displayed'):
                        kwargs['description'] = value
                        break
                    if not latest or last_modified > latest:
                        latest = last_modified
                        kwargs['description'] = value

            # APP-1766 - STIX spec requirement
            id_ = f'''{data.get('ownerName').lower()}-{_type.lower()}-{data.get('summary')}'''
            if id_.lower() == '00abedb4-aa42-466c-9c01-fed23315a9b7':
                self.logger.log.error(
                    'RESERVED UUID 00abedb4-aa42-466c-9c01-fed23315a9b7 '
                    f'created for indicator {data}'
                )
                continue
            kwargs['id'] = f'indicator--{uuid.uuid5(uuid.NAMESPACE_X500, id_)}'

            # {
            #     "type": "indicator",
            #     "spec_version": "2.1",
            #     "id": "indicator--78e53a5c-9510-4a95-88b1-dbac1ee60ca5",
            #     "created": "2020-09-08T19:16:25.481964Z",
            #     "modified": "2020-09-08T19:16:25.481964Z",
            #     "name": "TCI - kqvri.com",
            #     "description": "visible description",
            #     "indicator_types": [
            #         "malicious-activity"
            #     ],
            #     "pattern": "[domain-name:value = 'kqvri.com']",
            #     "pattern_type": "stix",
            #     "pattern_version": "2.1",
            #     "valid_from": "2020-09-08T19:16:25.481964Z",
            #     "labels": [
            #         "test1"
            #     ]
            # }

            try:
                rating = str(int(data.get('rating')))
                kwargs.setdefault('labels', []).append(self.x_threat_rating_map[rating])
            except Exception:  # nosec
                pass

            yield kwargs

    def consume_mappings(self, stix_data: dict, collection_id: str):
        """Produce ThreatConnect mappings from a STIX 2.1 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A array of indicator mappings.
        """
        mappings = []
        batch_xid_array = [stix_data.get('id')]
        if collection_id:
            batch_xid_array += [collection_id]
        try:
            indicators = self.stix_parser.parse(stix_data.get('pattern'))
            filtered_indicators = []
            for indicator in indicators:
                if not hasattr(indicator, 'path'):
                    self.logger.log.info(
                        '''Pattern not supported. '''
                        f'''Ignoring tree indicators for id: {stix_data.get('id')}.'''
                    )
                    continue
                filtered_indicators.append(indicator)
            indicators = filtered_indicators
            mappings = [
                self._default_consume_handler(indicators, batch_xid_array),
                self._ip_consume_handler(indicators, batch_xid_array),
                self._file_consume_handler(indicators, batch_xid_array),
            ]
            mappings = list(itertools.chain(*mappings))
        except Exception:
            self.logger.log.trace(
                f'''Pattern for Stix Object: {stix_data.get('id')} not parsed.'''
            )
        return mappings

    @staticmethod
    def _file_consume_handler(indicators: Iterable[Indicator], batch_xid_array):
        """Produce ThreatConnect file mappings from a list of STIX 2.1 indicators

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A array of indicator mappings.
        """
        file_indicators = list(filter(lambda i: 'file:hashes' in i.path, indicators))

        if len(file_indicators) <= 0:
            return []
        batch_xid_array.append('File')
        mappings = []
        # Changed logic to handle: APP-2560
        for i in file_indicators:
            mappings.append(
                {
                    'type': 'File',
                    'summary': i.value,
                    'confidence': '@.confidence',
                    'xid': Batch.generate_xid(batch_xid_array + [i.value]),
                }
            )
        return mappings

    @staticmethod
    def _ip_consume_handler(indicators: Iterable[Indicator], batch_xid_array):
        """Produce ThreatConnect Address/CIDR mappings from a list of STIX 2.1 indicators

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A array of indicator mappings.
        """
        mappings = []
        for i in filter(lambda i: i.path in ['ipv4-addr:value', 'ipv6-addr:value'], indicators):
            parse_map = None
            if i.path == 'ipv4-addr:value':
                if '/' in i.value and i.value.split('/')[1] != '32':  # this is a CIDR
                    parse_map = {
                        'type': 'CIDR',
                        'summary': i.value,
                    }
                else:  # this is an address
                    parse_map = {
                        'type': 'Address',
                        'summary': i.value.split('/')[0],
                    }
            elif i.path == 'ipv6-addr:value':
                if '/' in i.value and i.value.split('/')[1] != '128':  # this is a CIDR
                    parse_map = {
                        'type': 'CIDR',
                        'summary': i.value,
                    }
                else:  # this is an address
                    parse_map = {
                        'type': 'Address',
                        'summary': i.value.split('/')[0],
                    }
            parse_map['confidence'] = '@.confidence'
            parse_map['xid'] = Batch.generate_xid(
                batch_xid_array + [parse_map.get('type'), parse_map.get('summary')]
            )
            mappings.append(parse_map)
        return mappings

    @staticmethod
    def _default_consume_handler(indicators: Iterable[Indicator], batch_xid_array):
        """Produce ThreatConnect URL/EmailAddress/Host/ASN mappings from STIX 2.1 indicators

        Args:
            stix_data: STIX Indicator objects to parse.

        Returns:
            A array of indicator mappings.
        """

        type_map = {
            'url:value': 'URL',
            'email-addr:value': 'EmailAddress',
            'domain-name:value': 'Host',
            'autonomous-system:name': 'ASN',
            'email-message:subject': 'EmailSubject'
        }

        mappings = []
        for i in filter(lambda i: i.path in type_map.keys(), indicators):
            indicator_type = type_map.get(i.path)

            mappings.append(
                {
                    'type': indicator_type,
                    'summary': i.value,
                    'confidence': '@.confidence',
                    'xid': Batch.generate_xid(batch_xid_array + [indicator_type, i.value]),
                }
            )
        return mappings
