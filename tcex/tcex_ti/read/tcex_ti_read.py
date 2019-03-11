# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
from enum import Enum

try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3


from tcex.tcex_ti.read.mappings.indicator.indicator_types.address import Address
from tcex.tcex_ti.read.mappings.indicator.indicator_types.url import URL
from tcex.tcex_ti.read.mappings.indicator.indicator_types.email_address import EmailAddress
from tcex.tcex_ti.read.mappings.indicator.indicator_types.file import File
from tcex.tcex_ti.read.mappings.indicator.indicator_types.host import Host
from tcex.tcex_ti.read.mappings.group.group_types.adversarys import Adversary
from tcex.tcex_ti.read.mappings.group.group_types.campaign import Campaign
from tcex.tcex_ti.read.mappings.group.group_types.document import Document
from tcex.tcex_ti.read.mappings.group.group_types.email import Email
from tcex.tcex_ti.read.mappings.group.group_types.event import Event
from tcex.tcex_ti.read.mappings.group.group_types.incident import Incident
from tcex.tcex_ti.read.mappings.group.group_types.intrusion_set import IntrusionSet
from tcex.tcex_ti.read.mappings.group.group_types.report import Report
from tcex.tcex_ti.read.mappings.group.group_types.signature import Signature
from tcex.tcex_ti.read.mappings.group.group_types.threat import Threat
from tcex.tcex_ti.read.mappings.victim import Victim
from tcex.tcex_ti.read.mappings.indicator.tcex_ti_indicator import (
    custom_indicator_class_factory,
    Indicator,
)

# import local modules for dynamic reference
module = __import__(__name__)


class TiRead:
    def __init__(self, tcex):
        self.tcex = tcex
        self._gen_indicator_class()

    def address(self, owner, unique_id=None):
        return Address(self.tcex, owner, unique_id=unique_id)

    def url(self):
        return URL(self.tcex)

    def email_address(self):
        return EmailAddress(self.tcex)

    def file(self):
        return File(self.tcex)

    def host(self):
        return Host(self.tcex)

    def adversary(self):
        return Adversary(self.tcex)

    def campaign(self):
        return Campaign(self.tcex)

    def document(self):
        return Document(self.tcex)

    def event(self):
        return Event(self.tcex)

    def email(self):
        return Email(self.tcex)

    def incident(self):
        return Incident(self.tcex)

    def intrustion_set(self):
        return IntrusionSet(self.tcex)

    def report(self):
        return Report(self.tcex)

    def signature(self):
        return Signature(self.tcex)

    def threat(self):
        return Threat(self.tcex)


    def victim(self):
        return Victim(self.tcex)


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
