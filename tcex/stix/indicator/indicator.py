from typing import Union, List, Dict

from dendrol import Pattern
from dendrol.lang.STIXPatternVisitor import STIXPatternVisitor
from dendrol.lang.STIXPatternParser import STIXPatternParser
import ipaddress

from tcex.stix.model import StixModel


class STIXVisitor(STIXPatternVisitor):
    def __init__(self):
        super().__init__()
        self._indicators = []  # indicators that have been pulled out of this

    def visitPropTestEqual(self, ctx: STIXPatternParser.PropTestEqualContext):
        test = ctx.getText()
        eq_index = test.index('=')
        if eq_index:
            path, value = test[eq_index:], test[:eq_index]

            self._indicators.append({
                'path': path.strip(),
                'value': value[1:-2].strip()
            })
            return self.visitChildren(ctx)

    # TODO implement in operator

    @property
    def indicators(self):
        return self._indicators


class Indicator(StixModel):

    def produce(self, tc_data: Union[list, dict]):
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        type_map = {
            'Host': lambda data: f"[domain-name:value = '{data.get('summary')}']",
            'URL': lambda data: f"[url:value = '{data.get('summary')}']",
            'EmailAddress': lambda data: f"[email-addr:value = '{data.get('summary')}']",
            'ASN': lambda data: f"[autonomous-system:name = '{data.get('summary')}']",
            'Address': Indicator._address_producer_helper,
            'CIDR': Indicator._cidr_producer_helper,
            'File': Indicator._file_producer_helper,
        }

        for data in tc_data:
            yield type_map.get(data.get('type'))(data)  # TODO handle unsupported types

    def consume(self, stix_data: Union[list, dict]):
        """Produce a ThreatConnect object from a STIX 2.0 JSON object."""
        if not isinstance(stix_data, list):
            stix_data = [stix_data]

        for data in stix_data:
            signature = {
                'type': 'Signature',
                'xid': data.get('id'),
                'name': data.get('name'),  # TODO what should default be?
            }
            if data.get('pattern_type', 'stix') == 'stix':
                # We only parse indicators out of stix patterns...
                pattern = Pattern(data.get('pattern'))
                s = STIXVisitor()
                pattern.visit(s)

                yield from Indicator._default_consume_handler(s.indicators, signature)
                yield from Indicator._ip_consume_handler(s.indicators, signature)
                yield from Indicator._file_consume_handler(s.indicators, signature)

            yield signature

    @staticmethod
    def _default_consume_handler(stix_indicators: List[Dict[str, str]], signature):
        type_map = {
            'url:value': 'URL',
            'email-addr:value': 'EmailAddress',
            'domain-name:value': 'Host',
            'autonomous-system:name': 'ASN'
        }

        for i in filter(lambda i: i.get('path') in type_map.keys(), stix_indicators):
            path = i.get('path')
            value = i.get('value')
            type = type_map.get(path)

            yield {
                'type': type,
                'value': value,
                'xid': None,  # TODO gen xid
                'associatedGroups': [
                    {'groupXid': signature.get('xid')}
                ]
            }

    @staticmethod
    def _ip_consume_handler(stix_indicators: List[Dict[str, str]], signature):
        for i in filter(lambda i: i.get('path') in ['ipv4-addr:value', 'ipv6-addr:value'],
                        stix_indicators):
            path = i.get('path')
            value = i.get('value')
            if 'ipv4-addr:value' == path:
                if '/' in value and value.split('/')[1] != '32':  # this is a CIDR
                    yield {
                        'type': 'CIDR',
                        'summary': value,
                        'xid': None,  # TODO gen xid
                        'associatedGroups': [
                            {'groupXid': signature.get('xid')}
                        ]
                    }
                else:  # this is an address
                    yield {
                        'type': 'Address',
                        'summary': value,
                        'xid': None,  # TODO gen xid
                        'associatedGroups': [
                            {'groupXid': signature.get('xid')}
                        ]
                    }
            elif 'ipv6-addr:value' == path:
                if '/' in value and value.split('/')[1] != '132':  # this is a CIDR
                    yield {
                        'type': 'CIDR',
                        'summary': value,
                        'xid': None,  # TODO gen xid
                        'associatedGroups': [
                            {'groupXid': signature.get('xid')}
                        ]
                    }
                else:  # this is an address
                    yield {
                        'type': 'Address',
                        'summary': value,
                        'xid': None,  # TODO gen xid
                        'associatedGroups': [
                            {'groupXid': signature.get('xid')}
                        ]
                    }

    @staticmethod
    def _file_consume_handler(stix_indicators: List[Dict[str, str]], signature: dict):
        file_indicators = list(filter(lambda i: 'file:hashes' in i.get('path'), stix_indicators))

        sha256_indicators = list(filter(lambda i: 'SHA-156' in i.get('path'), file_indicators))
        sha2_indicators = list(filter(lambda i: 'SHA-1' in i.get('path'), file_indicators))
        md5_indicators = list(filter(lambda i: 'MD5' in i.get('path'), file_indicators))

        if len(file_indicators) <= 3 and len(sha256_indicators) <= 1 and len(
                sha2_indicators) <= 1 and len(md5_indicators) <= 1:
            value = ' : '.join([v.get('value') for v in file_indicators])
            yield {
                'type': 'File',
                'summary': value,
                'xid': None,  # TODO gen xid
                'associatedGroups': [
                    {'groupXid': signature.get('xid')}
                ]}
        else:
            for i in file_indicators:
                yield {
                    'type': 'File',
                    'value': i.get('value'),
                    'xid': None,  # TODO gen xid
                    'associatedGroups': [
                        {'groupXid': signature.get('xid')}
                    ]
                }

    @staticmethod
    def _address_producer_helper(data):
        if isinstance(ipaddress.ip_address(data.get('summary')), ipaddress.IPv6Address):
            return f"[ipv6-addr:value = '{data.get('summary')}']"
        else:
            return f"[ipv4-addr:value = '{data.get('summary')}']"

    @staticmethod
    def _cidr_producer_helper(data):
        if isinstance(ipaddress.ip_network(data.get('summary')), ipaddress.IPv6Interface):
            return f"[ipv6-addr:value = '{data.get('summary')}']"
        else:
            return f"[ipv4-addr:value = '{data.get('summary')}']"

    @staticmethod
    def _file_producer_helper(data):
        expressions = []
        for hash in data.get('summary').split(' : '):
            if len(hash) == 32:
                expressions.append(f"file.hashes.'MD5' = '{hash}'")
            elif len(hash) == 64:
                expressions.append(f"file.hashes.'SHA-256' = '{hash}'")
            else:
                expressions.append(f"file.hashes.'SHA-2' = '{hash}'")

        return f'[{" OR ".join(expressions)}]'
