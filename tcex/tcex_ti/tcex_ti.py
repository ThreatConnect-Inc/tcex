# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
import hashlib
import uuid
import inflect
from tcex.tcex_ti.mappings.indicator.tcex_ti_indicator import (
    custom_indicator_class_factory,
    Indicator,
)
from tcex.tcex_ti.mappings.indicator.indicator_types.address import Address
from tcex.tcex_ti.mappings.indicator.indicator_types.url import URL
from tcex.tcex_ti.mappings.indicator.indicator_types.email_address import EmailAddress
from tcex.tcex_ti.mappings.indicator.indicator_types.file import File
from tcex.tcex_ti.mappings.indicator.indicator_types.host import Host
from tcex.tcex_ti.mappings.group.group_types.adversarys import Adversary
from tcex.tcex_ti.mappings.group.group_types.campaign import Campaign
from tcex.tcex_ti.mappings.group.group_types.document import Document
from tcex.tcex_ti.mappings.group.group_types.email import Email
from tcex.tcex_ti.mappings.group.group_types.event import Event
from tcex.tcex_ti.mappings.group.group_types.incident import Incident
from tcex.tcex_ti.mappings.group.group_types.intrusion_set import IntrusionSet
from tcex.tcex_ti.mappings.group.group_types.report import Report
from tcex.tcex_ti.mappings.group.group_types.signature import Signature
from tcex.tcex_ti.mappings.group.group_types.threat import Threat
from tcex.tcex_ti.mappings.victim import Victim
from tcex.tcex_ti.mappings.tag import Tag
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group

p = inflect.engine()

# import local modules for dynamic reference
module = __import__(__name__)


class TcExTi(object):
    """ThreatConnect Threat Intelligence Module"""

    def __init__(self, tcex):
        """

        :param tcex:
        """
        self.tcex = tcex
        self._custom_indicator_classes = {}
        self._gen_indicator_class()

    def address(self, ip, **kwargs):
        """

        :param ip:
        :param kwargs:
        :return:
        """
        return Address(self.tcex, ip, **kwargs)

    def url(self, url, **kwargs):
        """

        :param url:
        :param kwargs:
        :return:
        """
        return URL(self.tcex, url, **kwargs)

    def email_address(self, address, **kwargs):
        """

        :param address:
        :param kwargs:
        :return:
        """
        return EmailAddress(self.tcex, address, **kwargs)

    def file(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        return File(self.tcex, **kwargs)

    def host(self, hostname, **kwargs):
        """

        :param hostname:
        :param kwargs:
        :return:
        """
        return Host(self.tcex, hostname, **kwargs)

    def indicator(self, indicator_type=None, **kwargs):
        """

        :param indicator_type:
        :param kwargs:
        """
        if not indicator_type:
            return Indicator(self.tcex, None, **kwargs)

        upper_indicator_type = indicator_type.upper()

        indicator = None
        if upper_indicator_type == 'ADDRESS':
            indicator = Address(self.tcex, **kwargs.pop('ip'), **kwargs)
        elif upper_indicator_type == 'EMAILADDRESS':
            indicator = EmailAddress(self.tcex, **kwargs.pop('address'), **kwargs)
        elif upper_indicator_type == 'FILE':
            indicator = File(self.tcex, **kwargs)
        elif upper_indicator_type == 'HOST':
            indicator = Host(self.tcex, **kwargs.pop('hostname'), **kwargs)
        elif upper_indicator_type == 'URL':
            indicator = URL(self.tcex, **kwargs.pop('url'), **kwargs)
        else:
            try:
                if upper_indicator_type in self._custom_indicator_classes.keys():
                    print('[{}]'.format(indicator_type))
                    custom_indicator_details = self._custom_indicator_classes[indicator_type]
                    value_fields = custom_indicator_details.get('value_fields')
                    c = getattr(module, custom_indicator_details.get('branch'))
                    if len(value_fields) == 1:
                        indicator = c(value_fields[0], **kwargs)
                    elif len(value_fields) == 2:
                        indicator = c(value_fields[0], value_fields[1], **kwargs)
                    elif len(value_fields) == 3:
                        indicator = c(value_fields[0], value_fields[2], **kwargs)
            except:
                print('[{}]'.format(globals()))
                return None
        return indicator


    # Verify that these two are needed since they ARE custom indicator types.
    # def asn(self, as_number, **kwargs):
    #     return ASN(self.tcex, as_number, **kwargs)
    #
    # def cidr(self, block, **kwargs):
    #     return CIDR(self.tcex, block, **kwargs)
    ##########################################################################

    def group(self, group_type=None, **kwargs):
        """

        :param group_type:
        :param kwargs:
        :return:
        """

        group = None
        if not group_type:
            group = Group(self.tcex, None, None, **kwargs)

        group_type = group_type.upper()
        if group_type == 'ADVERSARY':
            group = Adversary(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'CAMPAIGN':
            group = Campaign(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'DOCUMENT':
            group = Document(
                self.tcex, kwargs.pop('name', None), kwargs.pop('file_name', None), **kwargs
            )
        if group_type == 'EVENT':
            group = Event(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'EMAIL':
            group = Email(
                self.tcex,
                kwargs.pop('name', None),
                kwargs.pop('subject', None),
                kwargs.pop('header', None),
                kwargs.pop('body', None),
                **kwargs
            )
        if group_type == 'INCIDENT':
            group = Incident(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'INTRUSTION SET':
            group = IntrusionSet(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'REPORT':
            group = Report(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'SIGNATURE':
            group = Signature(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'THREAT':
            group = Threat(self.tcex, kwargs.pop('name', None), **kwargs)
        return group

    def adversary(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Adversary(self.tcex, name, **kwargs)

    def campaign(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Campaign(self.tcex, name, **kwargs)

    def document(self, name, file_name, **kwargs):
        """

        :param name:
        :param file_name:
        :param kwargs:
        :return:
        """
        return Document(self.tcex, name, file_name, **kwargs)

    def event(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Event(self.tcex, name, **kwargs)

    def email(self, name, subject, header, body, **kwargs):
        """

        :param name:
        :param subject:
        :param header:
        :param body:
        :param kwargs:
        :return:
        """
        return Email(self.tcex, name, subject, header, body, **kwargs)

    def incident(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Incident(self.tcex, name, **kwargs)

    def intrustion_set(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return IntrusionSet(self.tcex, name, **kwargs)

    def report(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Report(self.tcex, name, **kwargs)

    def signature(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Signature(self.tcex, name, **kwargs)

    def threat(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Threat(self.tcex, name, **kwargs)

    def victim(self, name, **kwargs):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Victim(self.tcex, name, **kwargs)

    def tag(self, name):
        """

        :param name:
        :param kwargs:
        :return:
        """
        return Tag(self.tcex, name)

    @staticmethod
    def generate_xid(identifier=None):
        """

        :param identifier:
        :return:
        """
        if identifier is None:
            identifier = str(uuid.uuid4())
        elif isinstance(identifier, list):
            identifier = '-'.join([str(i) for i in identifier])
            identifier = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
        return hashlib.sha256(identifier.encode('utf-8')).hexdigest()

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
            custom_class = custom_indicator_class_factory(
                entry.get('apiBranch'), entry.get('apiEntity'), Indicator, class_data, value_fields
            )

            custom_indicator_data = {'branch': entry.get('apiBranch'),
                                     'entry': entry.get('apiEntry'),
                                     'value_fields': value_fields}
            self._custom_indicator_classes[entry.get('name').upper()] = custom_indicator_data

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
