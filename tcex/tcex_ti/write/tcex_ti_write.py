# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
from enum import Enum

try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3


from tcex.tcex_ti.write.mappings.indicator.indicator_types.address import Address
from tcex.tcex_ti.write.mappings.indicator.indicator_types.url import URL
from tcex.tcex_ti.write.mappings.indicator.indicator_types.asn import ASN
from tcex.tcex_ti.write.mappings.indicator.indicator_types.cidr import CIDR
from tcex.tcex_ti.write.mappings.indicator.indicator_types.email_address import EmailAddress
from tcex.tcex_ti.write.mappings.indicator.indicator_types.file import File
from tcex.tcex_ti.write.mappings.indicator.indicator_types.host import Host
from tcex.tcex_ti.write.mappings.group.group_types.adversarys import Adversary
from tcex.tcex_ti.write.mappings.group.group_types.campaign import Campaign
from tcex.tcex_ti.write.mappings.group.group_types.document import Document
from tcex.tcex_ti.write.mappings.group.group_types.email import Email
from tcex.tcex_ti.write.mappings.group.group_types.event import Event
from tcex.tcex_ti.write.mappings.group.group_types.incident import Incident
from tcex.tcex_ti.write.mappings.group.group_types.intrusion_set import IntrusionSet
from tcex.tcex_ti.write.mappings.group.group_types.report import Report
from tcex.tcex_ti.write.mappings.group.group_types.signature import Signature
from tcex.tcex_ti.write.mappings.group.group_types.threat import Threat
from tcex.tcex_ti.write.mappings.victim import Victim
from tcex.tcex_ti.write.mappings.indicator.tcex_ti_indicator import (
    custom_indicator_class_factory,
    Indicator,
)

# import local modules for dynamic reference
module = __import__(__name__)



class SignatureType(Enum):
    SNORT = 'Snort'
    SURICATA = 'Suricata'
    YARA = 'YARA'
    CLAMAV = 'ClamAV'
    OPENIOC = 'OpenIOC'
    CYBOX = 'CybOX'
    BRO = 'Bro'
    REGEX = 'Regex'
    SPL = 'Splunk Search'


class TiWrite:
    def __init__(self, tcex):
        self.tcex = tcex
        self._gen_indicator_class()

    def address(self, ip, **kwargs):
        return Address(self.tcex, ip, **kwargs)

    def url(self, url, **kwargs):
        return URL(self.tcex, url, **kwargs)

    def email_address(self, address, **kwargs):
        return EmailAddress(self.tcex, address, **kwargs)

    def file(self, **kwargs):
        return File(self.tcex, **kwargs)

    def host(self, hostname, **kwargs):
        return Host(self.tcex, hostname, **kwargs)

    # Verify that these two are needed since they ARE custom indicator types.
    def asn(self, as_number, **kwargs):
        return ASN(self.tcex, as_number, **kwargs)

    def cidr(self, block, **kwargs):
        return CIDR(self.tcex, block, **kwargs)
    ##########################################################################

    def adversary(self, name, **kwargs):
        return Adversary(self.tcex, name, **kwargs)

    def campaign(self, name, **kwargs):
        return Campaign(self.tcex, name, **kwargs)

    def document(self, name, file_name, **kwargs):
        return Document(self.tcex, name, file_name, **kwargs)

    def event(self, name, **kwargs):
        return Event(self.tcex, name, **kwargs)

    def email(self, name, subject, header, body, **kwargs):
        return Email(self.tcex, name, subject, header, body, **kwargs)

    def incident(self, name, **kwargs):
        return Incident(self.tcex, name, **kwargs)

    def intrustion_set(self, name, **kwargs):
        return IntrusionSet(self.tcex, name, **kwargs)

    def report(self, name, **kwargs):
        return Report(self.tcex, name, **kwargs)

    def signature(self, name, **kwargs):
        return Signature(self.tcex, name, **kwargs)

    def threat(self, name, **kwargs):
        return Threat(self.tcex, name, **kwargs)


    def victim(self, name, **kwargs):
        return Victim(self.tcex, name, **kwargs)

    # def track(self, name, **kwargs):
    #     return Track(self.tcex, name, **kwargs)

    # def adversary(self, name, subject, header, body, **kwargs):
    #     return Adversary(name, subject, header, body, **kwargs)



    def _gen_indicator_class(self):
        """Generate Custom Indicator Classes."""

        for entry in self.tcex.indicator_types_data.values():
            name = entry.get('name')
            class_name = name.replace(' ', '')
            # temp fix for API issue where boolean are returned as strings
            entry['custom'] = self.tcex.utils.to_bool(entry.get('custom'))

            if class_name in globals():
                # skip Indicator Type if a class already exists
                continue

            # Custom Indicator can have 3 values. Only add the value if it is set.
            value_fields = []
            if entry.get('value1Label'):
                value_fields.append(entry['value1Label'])
            if entry.get('value2Label'):
                value_fields.append(entry['value2Label'])
            if entry.get('value3Label'):
                value_fields.append(entry['value3Label'])
            value_count = len(value_fields)

            if len(value_fields) == 0:
                continue

            class_data = {}
            # Add Class for each Custom Indicator type to this module
            custom_class = custom_indicator_class_factory(entry.get('apiBranch'), Indicator, class_data, value_fields)

            setattr(module, class_name, custom_class)

            # Add Custom Indicator Method
            self._gen_indicator_method(name, custom_class, value_count)

    def _gen_indicator_method(self, name, custom_class, value_count):
        """Dynamically generate custom Indicator methods.

        Args:
            name (str): The name of the method.
            custom_class (object): The class to add.
            value_count (int): The number of value parameters to support.
        """
        method_name = name.replace(' ', '_').lower()
        tcex = self.tcex

        # Add Method for each Custom Indicator class
        def method_1(value1, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, **kwargs)

        def method_2(value1, value2, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, value2, **kwargs)

        def method_3(value1, value2, value3, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, value2, value3, **kwargs)

        method = locals()['method_{}'.format(value_count)]
        setattr(self, method_name, method)