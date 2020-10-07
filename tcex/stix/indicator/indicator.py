"""Parser for STIX Indicator Objects.

import stix2
see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070633
"""
# standard library
import uuid
from typing import Dict, List, Union

# third-party
import stix2
from dendrol import Pattern
from dendrol.lang.STIXPatternListener import STIXPatternListener
from dendrol.lang.STIXPatternParser import STIXPatternParser

# first-party
from tcex.batch import Batch
from tcex.stix import StixModel  # pylint: disable=cyclic-import


class StixIndicator(StixModel):
    """Parser for STIX Indicator Objects.

    see: https://docs.oasis-open.org/cti/stix/v2.1/csprd01/stix-v2.1-csprd01.html#_Toc16070633
    """

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
            labels = []
            description = None
            latest = None
            for tag in data.get('tag', []):
                labels.append(tag.get('name'))
            for attribute in data.get('attribute', []):
                if attribute.get('type').lower() == 'description':
                    value = attribute.get('value')
                    last_modified = attribute.get('lastModified'), '%y-%m-%d'
                    if attribute.get('displayed'):
                        description = value
                        break
                    if not latest or latest > last_modified:
                        latest = last_modified
                        description = value

            id_ = f'''{data.get('ownerName').lower()}-{_type.lower()}-{data.get('summary')}'''
            self.logger.log.error(f'indicator--{id_}')
            id_ = uuid.uuid5(uuid.NAMESPACE_X500, id_)

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

            if data.get('rating', None) == 0:
                labels.append('Threat Rating: Unknown')
            elif data.get('rating', None) == 1:
                labels.append('Threat Rating: Suspicious')
            elif data.get('rating', None) == 2:
                labels.append('Threat Rating: Low')
            elif data.get('rating', None) == 3:
                labels.append('Threat Rating: Moderate')
            elif data.get('rating', None) == 4:
                labels.append('Threat Rating: High')
            elif data.get('rating', None) == 5:
                labels.append('Threat Rating: Very High')

            yield stix2.Indicator(
                confidence=data.get('confidence'),
                labels=labels,
                created=data.get('dateAdded'),
                modified=data.get('lastModified'),
                description=description,
                id=f'indicator--{id_}',
                name=f'{data.get("summary")}',
                lang='en',
                pattern_version='2.1',
                indicator_types=['malicious-activity'],
                pattern_type='stix',
                pattern=indicator_details.get('lambda')(data),
            )

    def consume(self, stix_data: Union[list, dict]):
        """Produce a ThreatConnect object from a STIX 2.0 JSON object.

        Args:
            stix_data: STIX Indicator objects to parse.

        Yields:
            A ThreatConnect Signature and optionally ThreatConnect indicators.
        """
        if not isinstance(stix_data, list):
            stix_data = [stix_data]

        for data in stix_data:
            if data.get('pattern_type', 'stix') != 'stix':
                continue

            signature = {
                'type': 'Signature',
                'xid': data.get('id'),
                'name': data.get('name'),
            }
            if data.get('pattern_type', 'stix') == 'stix':
                # We only parse indicators out of stix patterns...
                pattern = Pattern(data.get('pattern'))
                s = STIXListener()
                pattern.walk(s)

                yield from StixIndicator._default_consume_handler(s.indicators, signature)
                yield from StixIndicator._ip_consume_handler(s.indicators, signature)
                yield from StixIndicator._file_consume_handler(s.indicators, signature)

            yield signature

    @staticmethod
    def _default_consume_handler(stix_indicators: List[Dict[str, str]], signature):
        type_map = {
            'url:value': 'URL',
            'email-addr:value': 'EmailAddress',
            'domain-name:value': 'Host',
            'autonomous-system:name': 'ASN',
        }

        for i in filter(lambda i: i.get('path') in type_map.keys(), stix_indicators):
            path = i.get('path')
            value = i.get('value')
            indicator_type = type_map.get(path)

            yield {
                'type': indicator_type,
                'summary': value,
                'xid': Batch.generate_xid([signature.get('xid'), value]),
                'associatedGroups': [{'groupXid': signature.get('xid')}],
            }

    @staticmethod
    def _ip_consume_handler(stix_indicators: List[Dict[str, str]], signature):
        for i in filter(
            lambda i: i.get('path') in ['ipv4-addr:value', 'ipv6-addr:value'], stix_indicators
        ):
            path = i.get('path')
            value = i.get('value')
            if path == 'ipv4-addr:value':
                if '/' in value and value.split('/')[1] != '32':  # this is a CIDR
                    yield {
                        'type': 'CIDR',
                        'summary': value,
                        'xid': Batch.generate_xid([signature.get('xid'), value]),
                        'associatedGroups': [{'groupXid': signature.get('xid')}],
                    }
                else:  # this is an address
                    yield {
                        'type': 'Address',
                        'summary': value.split('/')[0],
                        'xid': Batch.generate_xid([signature.get('xid'), value]),
                        'associatedGroups': [{'groupXid': signature.get('xid')}],
                    }
            elif path == 'ipv6-addr:value':
                if '/' in value and value.split('/')[1] != '128':  # this is a CIDR
                    yield {
                        'type': 'CIDR',
                        'summary': value,
                        'xid': Batch.generate_xid([signature.get('xid'), value]),
                        'associatedGroups': [{'groupXid': signature.get('xid')}],
                    }
                else:  # this is an address
                    yield {
                        'type': 'Address',
                        'summary': value.split('/')[0],
                        'xid': Batch.generate_xid([signature.get('xid'), value]),
                        'associatedGroups': [{'groupXid': signature.get('xid')}],
                    }

    @staticmethod
    def _file_consume_handler(stix_indicators: List[Dict[str, str]], signature: dict):
        file_indicators = list(filter(lambda i: 'file:hashes' in i.get('path'), stix_indicators))

        sha256_indicators = list(
            filter(lambda i: 'SHA-156' in i.get('path').upper(), file_indicators)
        )
        sha2_indicators = list(filter(lambda i: 'SHA-1' in i.get('path').upper(), file_indicators))
        md5_indicators = list(filter(lambda i: 'MD5' in i.get('path').upper(), file_indicators))

        if len(file_indicators) > 0:
            if (
                len(file_indicators) <= 3
                and len(sha256_indicators) <= 1
                and len(sha2_indicators) <= 1
                and len(md5_indicators) <= 1
            ):
                value = ' : '.join([v.get('value') for v in file_indicators])
                yield {
                    'type': 'File',
                    'summary': value,
                    'xid': Batch.generate_xid([signature.get('xid'), value]),
                    'associatedGroups': [{'groupXid': signature.get('xid')}],
                }
            else:
                for i in file_indicators:
                    yield {
                        'type': 'File',
                        'summary': i.get('value'),
                        'xid': Batch.generate_xid([signature.get('xid'), i.get('value')]),
                        'associatedGroups': [{'groupXid': signature.get('xid')}],
                    }


class STIXListener(STIXPatternListener):
    """Visitor for the parsed stix pattern."""

    def __init__(self):
        """Visitor for the parsed stix pattern."""
        super().__init__()
        self._indicators = []  # indicators that have been pulled out of this

    def enterPropTestEqual(self, ctx: STIXPatternParser.PropTestEqualContext):
        """Pull out path and value from statements with =.

        Args:
            ctx: the context of the equals statement.
        """
        test = ctx.getText()
        eq_index = test.index('=')
        if eq_index:
            path, value = test[:eq_index], test[(eq_index + 1) :]  # noqa: E203

            self._indicators.append({'path': path.strip(), 'value': value.strip()[1:-1]})

    def enterPropTestSet(self, ctx: STIXPatternParser.PropTestParenContext):
        """Pull out path and value from statements with in (...).

        Args:
            ctx: the context of the equals statement.
        """
        text = ctx.getText()
        path, values = text.split('IN')

        path = path.strip()

        values = values[1:-1]  # strip off the surrounding parens.
        values = [v.strip()[1:-1] for v in values.split(',')]  # split on , and strip

        for value in values:
            self._indicators.append({'path': path, 'value': value})

    @property
    def indicators(self):
        """Return the indicators parsed out of this pattern."""
        return self._indicators
