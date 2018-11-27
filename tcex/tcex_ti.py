# -*- coding: utf-8 -*-
"""TcEx Threat Intelligence Module"""
# import hashlib
import json
# import math
# import os
import re
# import shelve
# import time
import uuid

from .tcex_utils import TcExUtils

# import local modules for dynamic reference
module = __import__(__name__)


def custom_indicator_class_factory(indicator_type, base_class, class_dict, value_fields):
    """Internal method for dynamically building Custom Indicator Class."""
    value_count = len(value_fields)

    def init_1(self, tcex, value1, xid, **kwargs):
        """Init method for Custom Indicator Types with one value"""
        summary = self.build_summary(value1)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, xid, **kwargs)
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_2(self, tcex, value1, value2, xid, **kwargs):
        """Init method for Custom Indicator Types with two values."""
        summary = self.build_summary(value1, value2)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, xid, **kwargs)
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_3(self, tcex, value1, value2, value3, xid, **kwargs):
        """Init method for Custom Indicator Types with three values."""
        summary = self.build_summary(value1, value2, value3)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, xid, **kwargs)
        for k, v in class_dict.items():
            setattr(self, k, v)

    class_name = indicator_type.replace(' ', '')
    init_method = locals()['init_{}'.format(value_count)]
    newclass = type(str(class_name), (base_class,), {"__init__": init_method})
    return newclass


class TcExTi(object):
    """TcEx Threat Intelligence Module"""

    def __init__(self, tcex, owner=None, ti_type=None, **kwargs):
        """Initialize Class properties.

        Args:
            tcex (obj): [description]
            owner (string;list, optional): Defaults to None. A single owner or list of owners.
            ti_type (string, optional): Defaults to None. The Threat Intelligence type.
        """

        self.tcex = tcex
        self._owner = owner
        self._ti_type = ti_type

        # build custom indicator classes
        # self._gen_indicator_class()

    # def _gen_indicator_class(self):
    #     """Generate Custom Indicator Classes."""

    #     for entry in self.tcex.indicator_types_data.values():
    #         name = entry.get('name')
    #         class_name = name.replace(' ', '')
    #         # temp fix for API issue where boolean are returned as strings
    #         entry['custom'] = self.tcex.utils.to_bool(entry.get('custom'))

    #         if class_name in globals():
    #             # skip Indicator Type if a class already exists
    #             continue

    #         # Custom Indicator can have 3 values. Only add the value if it is set.
    #         value_fields = []
    #         if entry.get('value1Label'):
    #             value_fields.append(entry['value1Label'])
    #         if entry.get('value2Label'):
    #             value_fields.append(entry['value2Label'])
    #         if entry.get('value3Label'):
    #             value_fields.append(entry['value3Label'])
    #         value_count = len(value_fields)

    #         class_data = {}
    #         # Add Class for each Custom Indicator type to this module
    #         custom_class = custom_indicator_class_factory(name, Indicator, class_data, value_fields)
    #         setattr(module, class_name, custom_class)

    #         # Add Custom Indicator Method
    #         self._gen_indicator_method(name, custom_class, value_count)

    # def _gen_indicator_method(self, name, custom_class, value_count):
    #     """Dynamically generate custom Indicator methods.

    #     Args:
    #         name (str): The name of the method.
    #         custom_class (object): The class to add.
    #         value_count (int): The number of value parameters to support.
    #     """
    #     method_name = name.replace(' ', '_').lower()

    #     # Add Method for each Custom Indicator class
    #     def method_1(value1, xid, **kwargs):
    #         """Add Custom Indicator data to Batch object"""
    #         indicator_obj = custom_class(value1, xid, **kwargs)
    #         return self._indicator(indicator_obj)

    #     def method_2(value1, value2, xid, **kwargs):
    #         """Add Custom Indicator data to Batch object"""
    #         indicator_obj = custom_class(value1, value2, xid, **kwargs)
    #         return self._indicator(indicator_obj)

    #     def method_3(value1, value2, value3, xid, **kwargs):
    #         """Add Custom Indicator data to Batch object"""
    #         indicator_obj = custom_class(value1, value2, value3, xid, **kwargs)
    #         return self._indicator(indicator_obj)

    #     method = locals()['method_{}'.format(value_count)]
    #     setattr(self, method_name, method)

    @staticmethod
    def _indicator_values(indicator):
        """Process indicators expanding file hashes/custom indicators into multiple entries.

        Args:
            indicator (str): " : " delimited string

        Returns:
            list: The list of indicators split on " : ".
        """
        indicator_list = [indicator]
        if indicator.count(' : ') > 0:
            # handle all multi-valued indicators types (file hashes and custom indicators)
            indicator_list = []

            # group 1 - lazy capture everything to first <space>:<space> or end of line
            iregx_pattern = r'^(.*?(?=\s\:\s|$))?'
            iregx_pattern += r'(?:\s\:\s)?'  # remove <space>:<space>
            # group 2 - look behind for <space>:<space>, lazy capture everything
            #           to look ahead (optional <space>):<space> or end of line
            iregx_pattern += r'((?<=\s\:\s).*?(?=(?:\s)?\:\s|$))?'
            iregx_pattern += r'(?:(?:\s)?\:\s)?'  # remove (optional <space>):<space>
            # group 3 - look behind for <space>:<space>, lazy capture everything
            #           to look ahead end of line
            iregx_pattern += r'((?<=\s\:\s).*?(?=$))?$'
            iregx = re.compile(iregx_pattern)

            indicators = iregx.search(indicator)
            if indicators is not None:
                indicator_list = list(indicators.groups())

        return indicator_list

    # def address(self, ip, **kwargs):
    #     """Add Address data to Batch object.

    #     Args:
    #         ip (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of Address.
    #     """
    #     indicator_obj = Address(ip, **kwargs)
    #     return self._indicator(indicator_obj)

    # def adversary(self, name, **kwargs):
    #     """Add Adversary data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Adversary.
    #     """
    #     group_obj = Adversary(name, **kwargs)
    #     return self._group(group_obj)

    # def asn(self, as_number, **kwargs):
    #     """Add ASN data to Batch object.

    #     Args:
    #         as_number (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of ASN.
    #     """
    #     indicator_obj = ASN(as_number, **kwargs)
    #     return self._indicator(indicator_obj)

    # def campaign(self, name, **kwargs):
    #     """Add Campaign data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         first_seen (str, kwargs): The first seen datetime expression for this Group.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Campaign.
    #     """
    #     group_obj = Campaign(name, **kwargs)
    #     return self._group(group_obj)

    # def cidr(self, block, **kwargs):
    #     """Add CIDR data to Batch object.

    #     Args:
    #         block (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of CIDR.
    #     """
    #     indicator_obj = CIDR(block, **kwargs)
    #     return self._indicator(indicator_obj)

    # def document(self, name, file_name, **kwargs):
    #     """Add Document data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         file_name (str): The name for the attached file for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         file_content (str;method, kwargs): The file contents or callback method to retrieve
    #                                            file content.
    #         malware (bool, kwargs): If true the file is considered malware.
    #         password (bool, kwargs): If malware is true a password for the zip archive is
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Document.
    #     """
    #     group_obj = Document(name, file_name, **kwargs)
    #     return self._group(group_obj)

    # def email(self, name, subject, header, body, **kwargs):
    #     """Add Email data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         subject (str): The subject for this Email.
    #         header (str): The header for this Email.
    #         body (str): The body for this Email.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         from_addr (str, kwargs): The **from** address for this Email.
    #         to_addr (str, kwargs): The **to** address for this Email.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Email.
    #     """
    #     group_obj = Email(name, subject, header, body, **kwargs)
    #     return self._group(group_obj)

    # def email_address(self, address, **kwargs):
    #     """Add Email Address data to Batch object.

    #     Args:
    #         address (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of EmailAddress.
    #     """
    #     indicator_obj = EmailAddress(address, **kwargs)
    #     return self._indicator(indicator_obj)

    # def event(self, name, **kwargs):
    #     """Add Event data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         event_date (str, kwargs): The event datetime expression for this Group.
    #         status (str, kwargs): The status for this Group.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Event.
    #     """
    #     group_obj = Event(name, **kwargs)
    #     return self._group(group_obj)

    # def file(self, md5=None, sha1=None, sha256=None, **kwargs):
    #     """Add File data to Batch object.

    #     .. note:: A least one file hash value must be specified.

    #     Args:
    #         md5 (str, optional): The md5 value for this Indicator.
    #         sha1 (str, optional): The sha1 value for this Indicator.
    #         sha256 (str, optional): The sha256 value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         size (str, kwargs): The file size for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of File.
    #     """
    #     indicator_obj = File(md5, sha1, sha256, **kwargs)
    #     return self._indicator(indicator_obj)

    def group(self, group_type, name, **kwargs):
        """Add Group data to Batch object.

        Args:
            group_type (str): The ThreatConnect define Group type.
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Group.
        """
        # group_obj = Group(group_type, name, **kwargs)
        # return self._group(group_obj)
        pass

    # def host(self, hostname, **kwargs):
    #     """Add Email Address data to Batch object.

    #     Args:
    #         hostname (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of Host.
    #     """
    #     indicator_obj = Host(hostname, **kwargs)
    #     return self._indicator(indicator_obj)

    # def incident(self, name, **kwargs):
    #     """Add Incident data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         event_date (str, kwargs): The event datetime expression for this Group.
    #         status (str, kwargs): The status for this Group.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Incident.
    #     """
    #     group_obj = Incident(name, **kwargs)
    #     return self._group(group_obj)

    # def indicator(self, indicator_type, summary, **kwargs):
    #     """Add Indicator data to Batch object.

    #     Args:
    #         indicator_type (str): The ThreatConnect define Indicator type.
    #         summary (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of Indicator.
    #     """
    #     indicator_obj = Indicator(indicator_type, summary, **kwargs)
    #     return self._indicator(indicator_obj)

    # def intrusion_set(self, name, **kwargs):
    #     """Add Intrusion Set data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of IntrusionSet.
    #     """
    #     group_obj = IntrusionSet(name, **kwargs)
    #     return self._group(group_obj)

    # def mutex(self, mutex, **kwargs):
    #     """Add Mutex data to Batch object.

    #     Args:
    #         mutex (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of Mutex.
    #     """
    #     indicator_obj = Mutex(mutex, **kwargs)
    #     return self._indicator(indicator_obj)

    # def registry_key(self, key_name, value_name, value_type, **kwargs):
    #     """Add Registry Key data to Batch object.

    #     Args:
    #         key_name (str): The key_name value for this Indicator.
    #         value_name (str): The value_name value for this Indicator.
    #         value_type (str): The value_type value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of Registry Key.
    #     """
    #     indicator_obj = RegistryKey(key_name, value_name, value_type, **kwargs)
    #     return self._indicator(indicator_obj)

    # def report(self, name, **kwargs):
    #     """Add Report data to Batch object.

    #     Args:
    #         name (str): The name for this Group.
    #         file_name (str): The name for the attached file for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         file_content (str;method, kwargs): The file contents or callback method to retrieve
    #             file content.
    #         publish_date (str, kwargs): The publish datetime expression for this Group.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Report.
    #     """
    #     group_obj = Report(name, **kwargs)
    #     return self._group(group_obj)

    # def signature(self, name, file_name, file_type, file_text, **kwargs):
    #     """Add Signature data to Batch object.

    #     Valid file_types:
    #     + Snort ®
    #     + Suricata
    #     + YARA
    #     + ClamAV ®
    #     + OpenIOC
    #     + CybOX ™
    #     + Bro
    #     + Regex
    #     + SPL - Splunk ® Search Processing Language

    #     Args:
    #         name (str): The name for this Group.
    #         file_name (str): The name for the attached signature for this Group.
    #         file_type (str): The signature type for this Group.
    #         file_text (str): The signature content for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Signature.
    #     """
    #     group_obj = Signature(name, file_name, file_type, file_text, **kwargs)
    #     return self._group(group_obj)

    # def threat(self, name, **kwargs):
    #     """Add Threat data to Batch object

    #     Args:
    #         name (str): The name for this Group.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         xid (str, kwargs): The external id for this Group.

    #     Returns:
    #         obj: An instance of Threat.
    #     """
    #     group_obj = Threat(name, **kwargs)
    #     return self._group(group_obj)

    # def user_agent(self, text, **kwargs):
    #     """Add User Agent data to Batch object

    #     Args:
    #         text (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of UserAgent.
    #     """
    #     indicator_obj = UserAgent(text, **kwargs)
    #     return self._indicator(indicator_obj)

    # def url(self, text, **kwargs):
    #     """Add URL Address data to Batch object.

    #     Args:
    #         text (str): The value for this Indicator.
    #         confidence (str, kwargs): The threat confidence for this Indicator.
    #         date_added (str, kwargs): The date timestamp the Indicator was created.
    #         last_modified (str, kwargs): The date timestamp the Indicator was last modified.
    #         rating (str, kwargs): The threat rating for this Indicator.
    #         xid (str, kwargs): The external id for this Indicator.

    #     Returns:
    #         obj: An instance of URL.
    #     """
    #     indicator_obj = URL(text, **kwargs)
    #     return self._indicator(indicator_obj)


class ThreatConnectIntelligence(object):
    """ThreatConnect Intelligence Class"""

    def __init__(self, _tcex, owner=None, ti_type=None, **kwargs):
        """Initialize class properties."""
        self.tcex = _tcex
        self.owner = owner
        if self.owner is None:
            self.owner = []
        elif isinstance(self.owner, string_types):
            self.owner = [owner]
        self.type = type

    def __iter__(self):
        """Paginate and iterate over Threat Intelligence Data."""
        for p in pagination:
            for ti in ti_data:
                # return the individual threat intelligence data
                yield ti


#
# Groups
#


class Group(object):
    """ThreatConnect Batch Group Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = [
    #     '_attributes',
    #     '_file_content',
    #     '_group_data',
    #     '_labels',
    #     '_name',
    #     '_processed',
    #     '_type',
    #     '_tags',
    #     '_utils']

    def __init__(self, group_type, name, **kwargs):
        """Initialize Class Properties.

        Args:
            group_type (str): The ThreatConnect define Group type.
            name (str): The name for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        self._utils = TcExUtils()
        self._name = name
        self._type = group_type
        self._group_data = {'name': name, 'type': group_type}
        # process all kwargs and update metadata field names
        for arg, value in kwargs.items():
            self.add_key_value(arg, value)
        # set xid to random and unique uuid4 value if not provided
        if kwargs.get('xid') is None:
            self._group_data['xid'] = str(uuid.uuid4())
        self._attributes = []
        self._labels = []
        self._file_content = None
        self._tags = []
        self._processed = False

    @property
    def _metadata_map(self):
        """Return metadata map for Group objects."""
        return {
            'date_added': 'dateAdded',
            'event_date': 'eventDate',
            'file_name': 'fileName',
            'file_text': 'fileText',
            'file_type': 'fileType',
            'first_seen': 'firstSeen',
            'from_addr': 'from',
            'publish_date': 'publishDate',
            'to_addr': 'to'
        }

    def add_file(self, filename, file_content):
        """Add a file for Document and Report types.

        Example::

            document = tcex.batch.group('Document', 'My Document')
            document.add_file('my_file.txt', 'my contents')

        Args:
            filename (str): The name of the file.
            file_content (bytes|method|str): The contents of the file or callback to get contents.
        """
        self._group_data['fileName'] = filename
        self._file_content = file_content

    def add_key_value(self, key, value):
        """Add custom field to Group object.

        .. note:: The key must be the exact name required by the batch schema.

        Example::

            document = tcex.batch.group('Document', 'My Document')
            document.add_key_value('fileName', 'something.pdf')

        Args:
            key (str): The field key to add to the JSON batch data.
            value (str): The field value to add to the JSON batch data.
        """
        key = self._metadata_map.get(key, key)
        if key in ['dateAdded', 'eventDate', 'firstSeen', 'publishDate']:
            self._group_data[key] = self._utils.format_datetime(
                value, date_format='%Y-%m-%dT%H:%M:%SZ')
        elif key == 'file_content':
            # file content arg is not part of Group JSON
            pass
        else:
            self._group_data[key] = value

    def association(self, group_xid):
        """Add association using xid value.

        Args:
            group_xid (str): The external id of the Group to associate.
        """
        self._group_data.setdefault('associatedGroupXid', []).append(group_xid)

    def attribute(
            self, attr_type, attr_value, displayed=False, source=None, unique=True, formatter=None):
        """Return instance of Attribute

        unique:
            * False - Attribute type:value can be duplicated.
            * 'Type' - Attribute type has to be unique (e.g., only 1 Description Attribute).
            * True - Attribute type:value combo must be unique.

        Args:
            attr_type (str): The ThreatConnect defined attribute type.
            attr_value (str): The value for this attribute.
            displayed (bool, default:false): If True the supported attribute will be marked for
                display.
            source (str, optional): The source value for this attribute.
            unique (bool|string, optional): Control attribute creation.
            formatter (method, optional): A method that takes a single attribute value and returns a
                single formatted value.

        Returns:
            obj: An instance of Attribute.
        """
        attr = Attribute(attr_type, attr_value, displayed, source, formatter)
        if unique == 'Type':
            for attribute_data in self._attributes:
                if attribute_data.type == attr_type:
                    self._attributes.remove(attribute_data)
                    break
            self._attributes.append(attr)
        elif unique is True:
            for attribute_data in self._attributes:
                if attribute_data.type == attr_type and attribute_data.value == attr.value:
                    attr = attribute_data
                    break
            else:
                self._attributes.append(attr)
        elif unique is False:
            self._attributes.append(attr)
        return attr

    @property
    def data(self):
        """Return Group data."""
        # add attributes
        if self._attributes:
            self._group_data['attribute'] = []
            for attr in self._attributes:
                if attr.valid:
                    self._group_data['attribute'].append(attr.data)
        # add security labels
        if self._labels:
            self._group_data['securityLabel'] = []
            for label in self._labels:
                self._group_data['securityLabel'].append(label.data)
        # add tags
        if self._tags:
            self._group_data['tag'] = []
            for tag in self._tags:
                if tag.valid:
                    self._group_data['tag'].append(tag.data)
        return self._group_data

    @property
    def date_added(self):
        """Return Group dateAdded."""
        return self._group_data.get('dateAdded')

    @date_added.setter
    def date_added(self, date_added):
        """Set Indicator dateAdded."""
        self._group_data['dateAdded'] = self._utils.format_datetime(
            date_added, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def file_data(self):
        """Return Group file (only supported for Document and Report)."""
        return {
            'fileContent': self._file_content,
            'fileName': self._group_data.get('fileName'),
            'type': self._group_data.get('type')
        }

    @property
    def name(self):
        """Return Group name."""
        return self._group_data.get('name')

    @property
    def processed(self):
        """Return processed value.

        .. note:: Processed value indicates that a group with this xid has already been processed.
        """
        return self._processed

    @processed.setter
    def processed(self, processed):
        """Set processed."""
        self._processed = processed

    def security_label(self, name, description=None, color=None):
        """Return instance of SecurityLabel.

        .. note:: The provided security label will be create if it doesn't exist. If the security
            label already exists nothing will be changed.

        Args:
            name (str): The value for this security label.
            description (str): A description for this security label.
            color (str): A color (hex value) for this security label.

        Returns:
            obj: An instance of SecurityLabel.
        """
        label = SecurityLabel(name, description, color)
        for label_data in self._labels:
            if label_data.name == name:
                label = label_data
                break
        else:
            self._labels.append(label)
        return label

    def tag(self, name, formatter=None):
        """Return instance of Tag.

        Args:
            name (str): The value for this tag.
            formatter (method, optional): A method that take a tag value and returns a
                formatted tag.

        Returns:
            obj: An instance of Tag.
        """
        tag = Tag(name, formatter)
        for tag_data in self._tags:
            if tag_data.name == name:
                tag = tag_data
                break
        else:
            self._tags.append(tag)
        return tag

    @property
    def type(self):
        """Return Group type."""
        return self._group_data.get('type')

    @property
    def xid(self):
        """Return Group xid."""
        return self._group_data.get('xid')

    def __str__(self):
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)


# class Adversary(Group):
#     """ThreatConnect Batch Adversary Object"""
#
#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []
#
#     def __init__(self, name, **kwargs):
#         """Initialize Class Properties.
#
#         Args:
#             name (str): The name for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Adversary, self).__init__('Adversary', name, **kwargs)

# class Campaign(Group):
#     """ThreatConnect Batch Campaign Object"""
#
#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []
#
#     def __init__(self, name, **kwargs):
#         """Initialize Class Properties.
#
#         Args:
#             name (str): The name for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             first_seen (str, kwargs): The first seen datetime expression for this Group.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Campaign, self).__init__('Campaign', name, **kwargs)
#
#     @property
#     def first_seen(self):
#         """Return Document first seen."""
#         return self._group_data.get('firstSeen')
#
#     @first_seen.setter
#     def first_seen(self, first_seen):
#         """Set Document first seen."""
#         self._group_data['firstSeen'] = self._utils.format_datetime(
#             first_seen, date_format='%Y-%m-%dT%H:%M:%SZ')

# class Document(Group):
#     """ThreatConnect Batch Document Object"""
#
#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = ['_file_data', '_group_data']
#
#     def __init__(self, name, file_name, **kwargs):
#         """Initialize Class Properties.
#
#         Args:
#             name (str): The name for this Group.
#             file_name (str): The name for the attached file for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             file_content (str;method, kwargs): The file contents or callback method to retrieve
#                                                file content.
#             malware (bool, kwargs): If true the file is considered malware.
#             password (bool, kwargs): If malware is true a password for the zip archive is required.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Document, self).__init__('Document', name, **kwargs)
#         self._group_data['fileName'] = file_name
#         # file data/content to upload
#         self._file_content = kwargs.get('file_content')
#
#     @property
#     def file_content(self):
#         """Return Group files."""
#         return self._file_content
#
#     @file_content.setter
#     def file_content(self, file_content):
#         """Set Document or Report file data."""
#         self._file_content = file_content
#
#     @property
#     def file_data(self):
#         """Return Group files."""
#         return {
#             'fileContent': self._file_content,
#             'fileName': self._group_data.get('fileName'),
#             'type': self._group_data.get('type')
#         }
#
#     @property
#     def malware(self):
#         """Return Document malware."""
#         return self._group_data.get('malware', False)
#
#     @malware.setter
#     def malware(self, malware):
#         """Set Document malware."""
#         self._group_data['malware'] = malware
#
#     @property
#     def password(self):
#         """Return Document password."""
#         return self._group_data.get('password', False)
#
#     @password.setter
#     def password(self, password):
#         """Set Document password."""
#         self._group_data['password'] = password

# class Email(Group):
#     """ThreatConnect Batch Email Object"""
#
#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []
#
#     def __init__(self, name, subject, header, body, **kwargs):
#         """Initialize Class Properties.
#
#         Args:
#             name (str): The name for this Group.
#             subject (str): The subject for this Email.
#             header (str): The header for this Email.
#             body (str): The body for this Email.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             from_addr (str, kwargs): The **from** address for this Email.
#             to_addr (str, kwargs): The **to** address for this Email.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Email, self).__init__('Email', name, **kwargs)
#         self._group_data['subject'] = subject
#         self._group_data['header'] = header
#         self._group_data['body'] = body
#         self._group_data['score'] = 0
#
#     @property
#     def from_addr(self):
#         """Return Email to."""
#         return self._group_data.get('to')
#
#     @from_addr.setter
#     def from_addr(self, from_addr):
#         """Set Email from."""
#         self._group_data['from'] = from_addr
#
#     @property
#     def score(self):
#         """Return Email to."""
#         return self._group_data.get('score')
#
#     @score.setter
#     def score(self, score):
#         """Set Email from."""
#         self._group_data['score'] = score
#
#     @property
#     def to_addr(self):
#         """Return Email to."""
#         return self._group_data.get('to')
#
#     @to_addr.setter
#     def to_addr(self, to_addr):
#         """Set Email to."""
#         self._group_data['to'] = to_addr

# class Event(Group):
#     """ThreatConnect Batch Event Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, name, **kwargs):
#         """Initialize Class Properties.

#         Valid Values:
#         + Escalated
#         + False Positive
#         + Needs Review
#         + No Further Action

#         Args:
#             name (str): The name for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             event_date (str, kwargs): The event datetime expression for this Group.
#             status (str, kwargs): The status for this Group.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Event, self).__init__('Event', name, **kwargs)

#     @property
#     def event_date(self):
#         """Return the Events "event date" value."""
#         return self._group_data.get('firstSeen')

#     @event_date.setter
#     def event_date(self, event_date):
#         """Set the Events "event date" value."""
#         self._group_data['eventDate'] = self._utils.format_datetime(
#             event_date, date_format='%Y-%m-%dT%H:%M:%SZ')

#     @property
#     def status(self):
#         """Return the Events status value."""
#         return self._group_data.get('status')

#     @status.setter
#     def status(self, status):
#         """Set the Events status value."""
#         self._group_data['status'] = status

# class Incident(Group):
#     """ThreatConnect Batch Incident Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, name, **kwargs):
#         """Initialize Class Properties.

#         Valid Values:
#         + Closed
#         + Containment Achieved
#         + Deleted
#         + Incident Reported
#         + Open
#         + New
#         + Rejected
#         + Restoration Achieved
#         + Stalled

#         Args:
#             name (str): The name for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             event_date (str, kwargs): The event datetime expression for this Group.
#             status (str, kwargs): The status for this Group.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Incident, self).__init__('Incident', name, **kwargs)

#     @property
#     def event_date(self):
#         """Return Incident event date."""
#         return self._group_data.get('eventDate')

#     @event_date.setter
#     def event_date(self, event_date):
#         """Set Incident event_date."""
#         self._group_data['eventDate'] = self._utils.format_datetime(
#             event_date, date_format='%Y-%m-%dT%H:%M:%SZ')

#     @property
#     def status(self):
#         """Return Incident status."""
#         return self._group_data.get('status')

#     @status.setter
#     def status(self, status):
#         """Set Incident status.

#         Valid Values:
#         + New
#         + Open
#         + Stalled
#         + Containment Achieved
#         + Restoration Achieved
#         + Incident Reported
#         + Closed
#         + Rejected
#         + Deleted
#         """
#         self._group_data['status'] = status

# class IntrusionSet(Group):
#     """ThreatConnect Batch Adversary Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, name, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             name (str): The name for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(IntrusionSet, self).__init__('Intrusion Set', name, **kwargs)

# class Report(Group):
#     """ThreatConnect Batch Report Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, name, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             name (str): The name for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             file_name (str, kwargs): The name for the attached file for this Group.
#             file_content (str;method, kwargs): The file contents or callback method to retrieve
#                                                file content.
#             publish_date (str, kwargs): The publish datetime expression for this Group.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Report, self).__init__('Report', name, **kwargs)
#         # file data/content to upload
#         self._file_content = kwargs.get('file_content')

#     @property
#     def file_content(self):
#         """Return Group files."""
#         return self._file_content

#     @file_content.setter
#     def file_content(self, file_content):
#         """Set Document or Report file data."""
#         self._file_content = file_content

#     @property
#     def file_data(self):
#         """Return Group files."""
#         return {
#             'fileContent': self._file_content,
#             'fileName': self._group_data.get('fileName'),
#             'type': self._group_data.get('type')
#         }

#     @property
#     def publish_date(self):
#         """Return Report publish date."""
#         return self._group_data.get('publishDate')

#     @publish_date.setter
#     def publish_date(self, publish_date):
#         """Set Report publish date"""
#         self._group_data['publishDate'] = self._utils.format_datetime(
#             publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')

# class Signature(Group):
#     """ThreatConnect Batch Signature Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, name, file_name, file_type, file_text, **kwargs):
#         """Initialize Class Properties.

#         Valid file_types:
#         + Snort ®
#         + Suricata
#         + YARA
#         + ClamAV ®
#         + OpenIOC
#         + CybOX ™
#         + Bro
#         + Regex
#         + SPL - Splunk ® Search Processing Language

#         Args:
#             name (str): The name for this Group.
#             file_name (str): The name for the attached signature for this Group.
#             file_type (str): The signature type for this Group.
#             file_text (str): The signature content for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Signature, self).__init__('Signature', name, **kwargs)
#         self._group_data['fileName'] = file_name
#         self._group_data['fileType'] = file_type
#         self._group_data['fileText'] = file_text

# class Threat(Group):
#     """ThreatConnect Batch Threat Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, name, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             name (str): The name for this Group.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             xid (str, kwargs): The external id for this Group.
#         """
#         super(Threat, self).__init__('Threat', name, **kwargs)

#
# Indicators
#

# class Indicator(object):
#     """ThreatConnect Batch Indicator Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = [
#     #     '_attributes',
#     #     '_file_actions',
#     #     '_indicator_data',
#     #     '_labels',
#     #     '_occurrences',
#     #     '_summary',
#     #     '_tags',
#     #     '_type',
#     #     '_utils']

#     def __init__(self, indicator_type, summary, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             indicator_type (str): The ThreatConnect define Indicator type.
#             summary (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         self._utils = TcExUtils()
#         self._summary = summary
#         self._type = indicator_type
#         self._indicator_data = {'summary': summary, 'type': indicator_type}
#         # process all kwargs and update metadata field names
#         for arg, value in kwargs.items():
#             self.add_key_value(arg, value)
#         # set xid to random and unique uuid4 value if not provided
#         if kwargs.get('xid') is None:
#             self._indicator_data['xid'] = str(uuid.uuid4())
#         self._attributes = []
#         self._file_actions = []
#         self._labels = []
#         self._occurrences = []
#         self._tags = []

#     @property
#     def _metadata_map(self):
#         """Return metadata map for Indicator objects."""
#         return {
#             'date_added': 'dateAdded',
#             'dnsActive': 'flag1',
#             'dns_active': 'flag1',
#             'last_modified': 'lastModified',
#             'private_flag': 'privateFlag',
#             'size': 'intValue1',
#             'whoisActive': 'flag2',
#             'whois_active': 'flag2'
#         }

#     def add_key_value(self, key, value):
#         """Add custom field to Indicator object.

#         .. note:: The key must be the exact name required by the batch schema.

#         Example::

#             file_hash = tcex.batch.file('File', '1d878cdc391461e392678ba3fc9f6f32')
#             file_hash.add_key_value('size', '1024')

#         Args:
#             key (str): The field key to add to the JSON batch data.
#             value (str): The field value to add to the JSON batch data.
#         """
#         key = self._metadata_map.get(key, key)
#         if key in ['dateAdded', 'lastModified']:
#             self._indicator_data[key] = self._utils.format_datetime(
#                 value, date_format='%Y-%m-%dT%H:%M:%SZ')
#         elif key == 'confidence':
#             self._indicator_data[key] = int(value)
#         elif key == 'rating':
#             self._indicator_data[key] = float(value)
#         else:
#             self._indicator_data[key] = value

#     @property
#     def active(self):
#         """Return Indicator active."""
#         return self._indicator_data.get('active')

#     @active.setter
#     def active(self, active):
#         """Set Indicator active."""
#         self._indicator_data['active'] = self._utils.to_bool(active)

#     def association(self, group_xid):
#         """Add association using xid value.

#         Args:
#             group_xid (str): The external id of the Group to associate.
#         """
#         association = {'groupXid': group_xid}
#         self._indicator_data.setdefault('associatedGroups', []).append(association)

#     def attribute(
#             self, attr_type, attr_value, displayed=False, source=None, unique=True, formatter=None):
#         """Return instance of Attribute

#         unique:
#             * False - Attribute type:value can be duplicated.
#             * Type - Attribute type has to be unique (e.g., only 1 Description Attribute).
#             * True - Attribute type:value combo must be unique.

#         Args:
#             attr_type (str): The ThreatConnect defined attribute type.
#             attr_value (str): The value for this attribute.
#             displayed (bool, default:false): If True the supported attribute will be marked for
#                 display.
#             source (str, optional): The source value for this attribute.
#             unique (bool|string, optional): Control attribute creation.
#             formatter (method, optional): A method that takes a single attribute value and returns a
#                 single formatted value.

#         Returns:
#             obj: An instance of Attribute.
#         """
#         attr = Attribute(attr_type, attr_value, displayed, source, formatter)
#         if unique == 'Type':
#             for attribute_data in self._attributes:
#                 if attribute_data.type == attr_type:
#                     attr = attribute_data
#                     break
#             else:
#                 self._attributes.append(attr)
#         elif unique is True:
#             for attribute_data in self._attributes:
#                 if attribute_data.type == attr_type and attribute_data.value == attr.value:
#                     attr = attribute_data
#                     break
#             else:
#                 self._attributes.append(attr)
#         elif unique is False:
#             self._attributes.append(attr)
#         return attr

#     def build_summary(self, val1=None, val2=None, val3=None):
#         """Build the Indicator summary using available values."""
#         summary = []
#         if val1 is not None:
#             summary.append(val1)
#         if val2 is not None:
#             summary.append(val2)
#         if val3 is not None:
#             summary.append(val3)
#         if not summary:
#             # Indicator object has no logger to output warning
#             pass
#         return ' : '.join(summary)

#     @property
#     def confidence(self):
#         """Return Indicator confidence."""
#         return self._indicator_data.get('confidence')

#     @confidence.setter
#     def confidence(self, confidence):
#         """Set Indicator confidence."""
#         self._indicator_data['confidence'] = int(confidence)

#     @property
#     def data(self):
#         """Return Indicator data."""
#         # add attributes
#         if self._attributes:
#             self._indicator_data['attribute'] = []
#             for attr in self._attributes:
#                 if attr.valid:
#                     self._indicator_data['attribute'].append(attr.data)
#         # add file actions
#         if self._file_actions:
#             self._indicator_data.setdefault('fileAction', {})
#             self._indicator_data['fileAction'].setdefault('children', [])
#             for action in self._file_actions:
#                 self._indicator_data['fileAction']['children'].append(action.data)
#         # add file occurrences
#         if self._occurrences:
#             self._indicator_data.setdefault('fileOccurrence', [])
#             for occurrence in self._occurrences:
#                 self._indicator_data['fileOccurrence'].append(occurrence.data)
#         # add security labels
#         if self._labels:
#             self._indicator_data['securityLabel'] = []
#             for label in self._labels:
#                 self._indicator_data['securityLabel'].append(label.data)
#         # add tags
#         if self._tags:
#             self._indicator_data['tag'] = []
#             for tag in self._tags:
#                 if tag.valid:
#                     self._indicator_data['tag'].append(tag.data)
#         return self._indicator_data

#     @property
#     def date_added(self):
#         """Return Indicator dateAdded."""
#         return self._indicator_data.get('dateAdded')

#     @date_added.setter
#     def date_added(self, date_added):
#         """Set Indicator dateAdded."""
#         self._indicator_data['dateAdded'] = self._utils.format_datetime(
#             date_added, date_format='%Y-%m-%dT%H:%M:%SZ')

#     @property
#     def last_modified(self):
#         """Return Indicator lastModified."""
#         return self._indicator_data.get('lastModified')

#     @last_modified.setter
#     def last_modified(self, last_modified):
#         """Set Indicator lastModified."""
#         self._indicator_data['lastModified'] = self._utils.format_datetime(
#             last_modified, date_format='%Y-%m-%dT%H:%M:%SZ')

#     def occurrence(self, file_name=None, path=None, date=None):
#         """Add a file Occurrence.

#         Args:
#             file_name (str, optional): The file name for this occurrence.
#             path (str, optional): The file path for this occurrence.
#             date (str, optional): The datetime expression for this occurrence.

#         Returns:
#             obj: An instance of Occurrence.
#         """
#         if self._indicator_data.get('type') != 'File':
#             # Indicator object has no logger to output warning
#             return

#         occurrence_obj = FileOccurrence(file_name, path, date)
#         self._occurrences.append(occurrence_obj)
#         return occurrence_obj

#     @property
#     def private_flag(self):
#         """Return Indicator private flag."""
#         return self._indicator_data.get('privateFlag')

#     @private_flag.setter
#     def private_flag(self, private_flag):
#         """Set Indicator private flag."""
#         self._indicator_data['privateFlag'] = self._utils.to_bool(private_flag)

#     @property
#     def rating(self):
#         """Return Indicator rating."""
#         return self._indicator_data.get('rating')

#     @rating.setter
#     def rating(self, rating):
#         """Set Indicator rating."""
#         self._indicator_data['rating'] = float(rating)

#     @property
#     def summary(self):
#         """Return Indicator summary."""
#         return self._indicator_data.get('summary')

#     def security_label(self, name, description=None, color=None):
#         """Return instance of SecurityLabel.

#         .. note:: The provided security label will be create if it doesn't exist. If the security
#             label already exists nothing will be changed.

#         Args:
#             name (str): The value for this security label.
#             description (str): A description for this security label.
#             color (str): A color (hex value) for this security label.

#         Returns:
#             obj: An instance of SecurityLabel.
#         """
#         label = SecurityLabel(name, description, color)
#         for label_data in self._labels:
#             if label_data.name == name:
#                 label = label_data
#                 break
#         else:
#             self._labels.append(label)
#         return label

#     def tag(self, name, formatter=None):
#         """Return instance of Tag.

#         Args:
#             name (str): The value for this tag.
#             formatter (method, optional): A method that take a tag value and returns a
#                 formatted tag.

#         Returns:
#             obj: An instance of Tag.
#         """
#         tag = Tag(name, formatter)
#         for tag_data in self._tags:
#             if tag_data.name == name:
#                 tag = tag_data
#                 break
#         else:
#             self._tags.append(tag)
#         return tag

#     @property
#     def type(self):
#         """Return Group type."""
#         return self._indicator_data.get('type')

#     @property
#     def xid(self):
#         """Return Group xid."""
#         return self._indicator_data.get('xid')

#     def __str__(self):
#         """Return string represtentation of object"""
#         return json.dumps(self.data, indent=4)

# class Address(Indicator):
#     """ThreatConnect Batch Address Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, ip, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             ip (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(Address, self).__init__('Address', ip, **kwargs)

# class ASN(Indicator):
#     """ThreatConnect Batch ASN Object."""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, as_number, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             as_number (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(ASN, self).__init__('ASN', as_number, **kwargs)

# class CIDR(Indicator):
#     """ThreatConnect Batch CIDR Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, block, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             block (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(CIDR, self).__init__('CIDR', block, **kwargs)

# class EmailAddress(Indicator):
#     """ThreatConnect Batch EmailAddress Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, address, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             address (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(EmailAddress, self).__init__('EmailAddress', address, **kwargs)

# class File(Indicator):
#     """ThreatConnect Batch File Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, md5=None, sha1=None, sha256=None, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             md5 (str, optional): The md5 value for this Indicator.
#             sha1 (str, optional): The sha1 value for this Indicator.
#             sha256 (str, optional): The sha256 value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             size (str, kwargs): The file size for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         summary = self.build_summary(md5, sha1, sha256)  # build the indicator summary
#         super(File, self).__init__('File', summary, **kwargs)
#         # self._file_action = []

#     def action(self, relationship):
#         """Add a File Action."""
#         action_obj = FileAction(self._indicator_data.get('xid'), relationship)
#         self._file_actions.append(action_obj)
#         return action_obj

#     @property
#     def md5(self):
#         """Return Indicator md5."""
#         return self._indicator_data.get('md5')

#     @md5.setter
#     def md5(self, md5):
#         """Set Indicator md5."""
#         self._indicator_data['md5'] = md5

#     @property
#     def sha1(self):
#         """Return Indicator sha1."""
#         return self._indicator_data.get('sha1')

#     @sha1.setter
#     def sha1(self, sha1):
#         """Set Indicator sha1."""
#         self._indicator_data['sha1'] = sha1

#     @property
#     def sha256(self):
#         """Return Indicator sha256."""
#         return self._indicator_data.get('sha256')

#     @sha256.setter
#     def sha256(self, sha256):
#         """Set Indicator sha256."""
#         self._indicator_data['sha256'] = sha256

#     @property
#     def size(self):
#         """Return Indicator size."""
#         return self._indicator_data.get('intValue1')

#     @size.setter
#     def size(self, size):
#         """Set Indicator size."""
#         self._indicator_data['intValue1'] = size

# class Host(Indicator):
#     """ThreatConnect Batch Host Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, hostname, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             hostname (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
#             whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(Host, self).__init__('Host', hostname, **kwargs)

#     @property
#     def dns_active(self):
#         """Return Indicator dns active."""
#         return self._indicator_data.get('flag1')

#     @dns_active.setter
#     def dns_active(self, dns_active):
#         """Set Indicator dns active."""
#         self._indicator_data['flag1'] = dns_active

#     @property
#     def whois_active(self):
#         """Return Indicator whois active."""
#         return self._indicator_data.get('flag2')

#     @whois_active.setter
#     def whois_active(self, whois_active):
#         """Set Indicator whois active."""
#         self._indicator_data['flag2'] = whois_active

# class Mutex(Indicator):
#     """ThreatConnect Batch Mutex Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, mutex, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             mutex (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(Mutex, self).__init__('Mutex', mutex, **kwargs)

# class RegistryKey(Indicator):
#     """ThreatConnect Batch Registry Key Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, key_name, value_name, value_type, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             key_name (str): The key_name value for this Indicator.
#             value_name (str): The value_name value for this Indicator.
#             value_type (str): The value_type value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         summary = self.build_summary(key_name, value_name, value_type)
#         super(RegistryKey, self).__init__('Registry Key', summary, **kwargs)

# class URL(Indicator):
#     """ThreatConnect Batch URL Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, text, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             text (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(URL, self).__init__('URL', text, **kwargs)

# class UserAgent(Indicator):
#     """ThreatConnect Batch User Agent Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = []

#     def __init__(self, text, **kwargs):
#         """Initialize Class Properties.

#         Args:
#             text (str): The value for this Indicator.
#             active (bool, kwargs): If False the indicator is marked "inactive" in TC.
#             confidence (str, kwargs): The threat confidence for this Indicator.
#             date_added (str, kwargs): The date timestamp the Indicator was created.
#             last_modified (str, kwargs): The date timestamp the Indicator was last modified.
#             private_flag (bool, kwargs): If True the indicator is marked as private in TC.
#             rating (str, kwargs): The threat rating for this Indicator.
#             xid (str, kwargs): The external id for this Indicator.
#         """
#         super(UserAgent, self).__init__('User Agent', text, **kwargs)

#
# Metadata Classes
#


class Attribute(object):
    """ThreatConnect Batch Attribute Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = ['_attribute_data', '_valid']

    def __init__(self, attr_type, attr_value, displayed=False, source=None, formatter=None):
        """Initialize Class Properties.

        Args:
            attr_type (str): The ThreatConnect defined attribute type.
            attr_value (str): The value for this attribute.
            displayed (bool, default:false): If True the supported attribute will be marked for
                display.
            source (str, optional): The source value for this attribute.
            formatter (method, optional): A method that take a single attribute value and return a
                single formatted value.
        """
        self._attribute_data = {'type': attr_type}
        if displayed:
            self._attribute_data['displayed'] = displayed
        # format the value
        if formatter is not None:
            attr_value = formatter(attr_value)
        self._attribute_data['value'] = attr_value
        # add source if provided
        if source is not None:
            self._attribute_data['source'] = source
        # is attr_value not null or ''
        self._valid = True
        # check for None and '' value only.
        if attr_value in [None, '']:
            self._valid = False

    @property
    def data(self):
        """Return Attribute data."""
        return self._attribute_data

    @property
    def displayed(self):
        """Return Attribute displayed."""
        return self._attribute_data.get('displayed')

    @displayed.setter
    def displayed(self, displayed):
        """Set Attribute displayed."""
        self._attribute_data['displayed'] = displayed

    @property
    def source(self):
        """Return Attribute source."""
        return self._attribute_data.get('source')

    @source.setter
    def source(self, source):
        """Set Attribute source."""
        self._attribute_data['source'] = source

    @property
    def type(self):
        """Return attribute value."""
        return self._attribute_data.get('type')

    @property
    def valid(self):
        """Return valid value."""
        return self._valid

    @property
    def value(self):
        """Return attribute value."""
        return self._attribute_data.get('value')

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)


# class FileAction(object):
#     """ThreatConnect Batch FileAction Object"""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = ['_action_data', '_children', 'xid']

#     def __init__(self, parent_xid, relationship):
#         """Initialize Class Properties.

#         .. warning:: This code is not complete and may require some update to the API.

#         Args:
#             parent_xid (str): The external id of the parent Indicator.
#             relationship: ???
#         """
#         self.xid = str(uuid.uuid4())
#         self._action_data = {
#             'indicatorXid': self.xid,
#             'relationship': relationship,
#             'parentIndicatorXid': parent_xid
#         }
#         self._children = []

#     @property
#     def data(self):
#         """Return File Occurrence data."""
#         if self._children:
#             for child in self._children:
#                 self._action_data.setdefault('children', []).append(child.data)
#         return self._action_data

#     def action(self, relationship):
#         """Add a nested File Action."""
#         action_obj = FileAction(self.xid, relationship)
#         self._children.append(action_obj)

#     def __str__(self):
#         """Return string represtentation of object."""
#         return json.dumps(self.data, indent=4)

# class FileOccurrence(object):
#     """ThreatConnect Batch FileAction Object."""

#     # TODO: enable when support for py2 is dropped.
#     # __slots__ = ['_occurrence_data', '_utils']

#     def __init__(self, file_name=None, path=None, date=None):
#         """Initialize Class Properties

#         Args:
#             file_name (str, optional): The file name for this occurrence.
#             path (str, optional): The file path for this occurrence.
#             date (str, optional): The datetime expression for this occurrence.
#         """
#         self._utils = TcExUtils()
#         self._occurrence_data = {}
#         if file_name is not None:
#             self._occurrence_data['fileName'] = file_name
#         if path is not None:
#             self._occurrence_data['path'] = path
#         if date is not None:
#             self._occurrence_data['date'] = self._utils.format_datetime(
#                 date, date_format='%Y-%m-%dT%H:%M:%SZ')

#     @property
#     def data(self):
#         """Return File Occurrence data."""
#         return self._occurrence_data

#     @property
#     def date(self):
#         """Return File Occurrence date."""
#         return self._occurrence_data.get('date')

#     @date.setter
#     def date(self, date):
#         """Set File Occurrence date."""
#         self._occurrence_data['date'] = self._utils.format_datetime(
#             date, date_format='%Y-%m-%dT%H:%M:%SZ')

#     @property
#     def file_name(self):
#         """Return File Occurrence file name."""
#         return self._occurrence_data.get('fileName')

#     @file_name.setter
#     def file_name(self, file_name):
#         """Set File Occurrence file name."""
#         self._occurrence_data['fileName'] = file_name

#     @property
#     def path(self):
#         """Return File Occurrence path."""
#         return self._occurrence_data.get('path')

#     @path.setter
#     def path(self, path):
#         """Set File Occurrence path."""
#         self._occurrence_data['path'] = path

#     def __str__(self):
#         """Return string represtentation of object."""
#         return json.dumps(self.data, indent=4)


class SecurityLabel(object):
    """ThreatConnect Batch SecurityLabel Object."""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = ['_label_data']

    def __init__(self, name, description=None, color=None):
        """Initialize Class Properties.

        Args:
            name (str): The value for this security label.
            description (str): A description for this security label.
            color (str): A color (hex value) for this security label.
        """
        self._label_data = {'name': name}
        # add description if provided
        if description is not None:
            self._label_data['description'] = description
        if color is not None:
            self._label_data['color'] = color

    @property
    def color(self):
        """Return Security Label color."""
        return self._label_data.get('color')

    @color.setter
    def color(self, color):
        """Set Security Label color."""
        self._label_data['color'] = color

    @property
    def data(self):
        """Return Security Label data."""
        return self._label_data

    @property
    def description(self):
        """Return Security Label description."""
        return self._label_data.get('description')

    @description.setter
    def description(self, description):
        """Set Security Label description."""
        self._label_data['description'] = description

    @property
    def name(self):
        """Return Security Label name."""
        return self._label_data.get('name')

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)


class Tag(object):
    """ThreatConnect Batch Tag Object"""

    # TODO: enable when support for py2 is dropped.
    # __slots__ = ['_tag_data', '_valid']

    def __init__(self, name, formatter=None):
        """Initialize Class Properties.

        Args:
            name (str): The value for this tag.
            formatter (method, optional): A method that take a tag value and returns a
                formatted tag.
        """
        if formatter is not None:
            name = formatter(name)
        self._tag_data = {'name': name}
        # is tag not null or ''
        self._valid = True
        if not name:
            self._valid = False

    @property
    def data(self):
        """Return Tag data."""
        return self._tag_data

    @property
    def name(self):
        """Return Tag name."""
        return self._tag_data.get('name')

    @property
    def valid(self):
        """Return valid data."""
        return self._valid

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)
