# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
import hashlib
import json
import math
import os
import re
import shelve
import time
import uuid

try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3

from .tcex_ti_indicator import (
    custom_indicator_class_factory,
    Indicator,
    Address,
    ASN,
    CIDR,
    EmailAddress,
    File,
    Host,
    Mutex,
    RegistryKey,
    URL,
    UserAgent,
)
from .tcex_ti_group import (
    Group,
    Adversary,
    Campaign,
    Document,
    Email,
    Event,
    Incident,
    IntrusionSet,
    Report,
    Signature,
    Threat,
)

# import local modules for dynamic reference
module = __import__(__name__)


class TcExTi(object):
    """ThreatConnect Threat Intelligence Module"""

    def __init__(self, tcex):
        """Initialize Class Properties.

        Args:
            tcex (obj): An instance of TcEx object.
        """
        self.tcex = tcex
        self._batch_max_chunk = 5000

        # instance
        self._batch = None
        self._v2 = None

        # shelf settings
        self._group_shelf_fqfn = None
        self._indicator_shelf_fqfn = None

        # global overrides on batch/file errors
        self._halt_on_batch_error = None
        self._halt_on_file_error = None
        self._halt_on_poll_error = None

        # stored flags
        self._saved_xids = None
        self._stored_groups = None  # indicates groups shelf file was provided
        self._stored_indicators = None  # indicates indicators shelf file was provided
        self.enable_saved_file = False

        # containers
        self._files = {}
        self._groups = None
        self._groups_shelf = None
        self._indicators = None
        self._indicators_shelf = None

        # build custom indicator classes
        self._gen_indicator_class()

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

            class_data = {}
            # Add Class for each Custom Indicator type to this module
            custom_class = custom_indicator_class_factory(name, Indicator, class_data, value_fields)
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

        # Add Method for each Custom Indicator class
        def method_1(value1, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, **kwargs)
            return self._indicator(indicator_obj)

        def method_2(value1, value2, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, value2, **kwargs)
            return self._indicator(indicator_obj)

        def method_3(value1, value2, value3, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, value2, value3, **kwargs)
            return self._indicator(indicator_obj)

        method = locals()['method_{}'.format(value_count)]
        setattr(self, method_name, method)

    def _group(self, group_data):
        """Return previously stored group or new group.

        Args:
            group_data (dict|obj): An Group dict or instance of Group object.

        Returns:
            dict|obj: The new Group dict/object or the previously stored dict/object.
        """
        if isinstance(group_data, dict):
            # get xid from dict
            xid = group_data.get('xid')
        else:
            # get xid from object
            xid = group_data.xid

        if self.groups.get(xid) is not None:
            # return existing group from memory
            group_data = self.groups.get(xid)
        elif self.groups_shelf.get(xid) is not None:
            # return existing group from shelf
            group_data = self.groups_shelf.get(xid)
        else:
            # store new group
            self.groups[xid] = group_data
        return group_data

    def _indicator(self, indicator_data):
        """Return previously stored indicator or new indicator.

        Args:
            indicator_data (dict|obj): An Indicator dict or instance of Indicator object.

        Returns:
            dict|obj: The new Indicator dict/object or the previously stored dict/object.

        """
        if isinstance(indicator_data, dict):
            # get xid from dict
            xid = indicator_data.get('xid')
        else:
            # get xid from object
            xid = indicator_data.xid

        if self.indicators.get(xid) is not None:
            # return existing indicator from memory
            indicator_data = self.indicators.get(xid)
        elif self.indicators_shelf.get(xid) is not None:
            # return existing indicator from shelf
            indicator_data = self.indicators_shelf.get(xid)
        else:
            # store new indicators
            self.indicators[xid] = indicator_data
        return indicator_data

    @staticmethod
    def _indicator_values(indicator):
        """Process indicators expanding file hashes/custom indicators into multiple entries.

        Args:
            indicator (str): Indicator with format " : " delimited string.

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

    def add_group(self, group_data):
        """Add a group to Batch Job.

        .. code-block:: javascript

            {
                "name": "Example Incident",
                "type": "Incident",
                "attribute": [{
                    "type": "Description",
                    "displayed": false,
                    "value": "Example Description"
                }],
                "xid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904",
                "associatedGroupXid": [
                    "e336e2dd-5dfb-48cd-a33a-f8809e83e904:58",
                ],
                "tag": [{
                    "name": "China"
                }]
            }

        Args:
            group_data (dict): The full Group data including attributes, labels, tags, and
                associations.
        """
        return self._group(group_data)

    def add_indicator(self, indicator_data):
        """Add an indicator to Batch Job.

        .. code-block:: javascript

            {
                "type": "File",
                "rating": 5.00,
                "confidence": 50,
                "summary": "53c3609411c83f363e051d455ade78a7
                            : 57a49b478310e4313c54c0fee46e4d70a73dd580
                            : db31cb2a748b7e0046d8c97a32a7eb4efde32a0593e5dbd58e07a3b4ae6bf3d7",
                "associatedGroups": [
                    {
                        "groupXid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904"
                    }
                ],
                "attribute": [{
                    "type": "Source",
                    "displayed": true,
                    "value": "Malware Analysis provided by external AMA."
                }],
                "fileOccurrence": [{
                    "fileName": "drop1.exe",
                    "date": "2017-03-03T18:00:00-06:00"
                }],
                "tag": [{
                    "name": "China"
                }],
                "xid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904:170139"
            }

        Args:
            indicator_data (dict): The Full Indicator data including attributes, labels, tags,
                and associations.
        """
        if indicator_data.get('type') not in ['Address', 'EmailAddress', 'File', 'Host', 'URL']:
            # for custom indicator types the valueX fields are required.
            # using the summary we can build the values
            index = 1
            for value in self._indicator_values(indicator_data.get('summary')):
                indicator_data['value{}'.format(index)] = value
                index += 1
        if indicator_data.get('type') == 'File':
            # convert custom field name to the appropriate value for batch v2
            size = indicator_data.pop('size', None)
            if size is not None:
                indicator_data['intValue1'] = size
        if indicator_data.get('type') == 'Host':
            # convert custom field name to the appropriate value for batch v2
            dns_active = indicator_data.pop('dnsActive', None)
            if dns_active is not None:
                indicator_data['flag1'] = dns_active
            whois_active = indicator_data.pop('whoisActive', None)
            if whois_active is not None:
                indicator_data['flag2'] = whois_active
        return self._indicator(indicator_data)

    def address(self, ip, **kwargs):
        """Add Address data to Batch object.

        Args:
            ip (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of Address.
        """
        indicator_obj = Address(ip, **kwargs)
        return self._indicator(indicator_obj)

    def adversary(self, name, **kwargs):
        """Add Adversary data to Batch object.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Adversary.
        """
        group_obj = Adversary(name, **kwargs)
        return self._group(group_obj)

    def asn(self, as_number, **kwargs):
        """Add ASN data to Batch object.

        Args:
            as_number (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of ASN.
        """
        indicator_obj = ASN(as_number, **kwargs)
        return self._indicator(indicator_obj)

    @property
    def batch(self):
        """Instance of BatchSubmit"""
        if self._batch is None:
            self._batch = TiBatchCreate(self)
        return self._batch

    def campaign(self, name, **kwargs):
        """Add Campaign data to Batch object.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            first_seen (str, kwargs): The first seen datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Campaign.
        """
        group_obj = Campaign(name, **kwargs)
        return self._group(group_obj)

    def cidr(self, block, **kwargs):
        """Add CIDR data to Batch object.

        Args:
            block (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of CIDR.
        """
        indicator_obj = CIDR(block, **kwargs)
        return self._indicator(indicator_obj)

    def close(self):
        """Cleanup batch job."""
        self.groups_shelf.close()
        self.indicators_shelf.close()
        if self.debug and self.enable_saved_file:
            fqfn = os.path.join(self.tcex.args.tc_temp_path, 'xids-saved')
            if os.path.isfile(fqfn):
                os.remove(fqfn)  # remove previous file to prevent duplicates
            with open(fqfn, 'w') as fh:
                for xid in self.saved_xids:
                    fh.write('{}\n'.format(xid))
        else:
            # delete saved files
            if os.path.isfile(self.group_shelf_fqfn):
                os.remove(self.group_shelf_fqfn)
            if os.path.isfile(self.group_shelf_fqfn):
                os.remove(self.indicator_shelf_fqfn)

    @property
    def data(self):
        """Return the batch data to be sent to the ThreatConnect API.

        **Processing Order:**
        * Process groups in memory up to max batch size.
        * Process groups in shelf to max batch size.
        * Process indicators in memory up to max batch size.
        * Process indicators in shelf up to max batch size.

        This method will remove the group/indicator from memory and/or shelf.
        """
        entity_count = 0
        data = {'group': [], 'indicator': []}
        # process group data
        group_data, entity_count = self.data_groups(self.groups, entity_count)
        data['group'].extend(group_data)
        if entity_count >= self._batch_max_chunk:
            return data
        group_data, entity_count = self.data_groups(self.groups_shelf, entity_count)
        data['group'].extend(group_data)
        if entity_count >= self._batch_max_chunk:
            return data

        # process indicator data
        indicator_data, entity_count = self.data_indicators(self.indicators, entity_count)
        data['indicator'].extend(indicator_data)
        if entity_count >= self._batch_max_chunk:
            return data
        indicator_data, entity_count = self.data_indicators(self.indicators_shelf, entity_count)
        data['indicator'].extend(indicator_data)
        if entity_count >= self._batch_max_chunk:
            return data
        return data

    def data_group_association(self, xid):
        """Return group dict array recursing over all associations.

        Args:
            xid (str): The xid of the group to retrieve associations.

        Returns:
            list: A list of group dicts.
        """
        groups = []
        group_data = None

        # get group data from one of the arrays
        if self.groups.get(xid) is not None:
            group_data = self.groups.get(xid)
            del self.groups[xid]
        elif self.groups_shelf.get(xid) is not None:
            group_data = self.groups_shelf.get(xid)
            del self.groups_shelf[xid]

        if group_data is not None:
            # convert any obj into dict and process file data
            group_data = self.data_group_type(group_data)
            groups.append(group_data)

            # recursively get associations
            for assoc_xid in group_data.get('associatedGroupXid', []):
                groups.extend(self.data_group_association(assoc_xid))

        return groups

    def data_group_type(self, group_data):
        """Return dict representation of group data.

        Args:
            group_data (dict|obj): The group data dict or object.

        Returns:
            dict: The group data in dict format.
        """
        if isinstance(group_data, dict):
            # process file content
            file_content = group_data.pop('fileContent', None)
            if file_content is not None:
                self._files[group_data.get('xid')] = {
                    'fileContent': file_content,
                    'type': group_data.get('type'),
                }
        else:
            GROUPS_STRINGS_WITH_FILE_CONTENTS = ['Document', 'Report']
            # process file content
            if group_data.data.get('type') in GROUPS_STRINGS_WITH_FILE_CONTENTS:
                self._files[group_data.data.get('xid')] = group_data.file_data
            group_data = group_data.data
        return group_data

    def data_groups(self, groups, entity_count):
        """Process Group data.

        Args:
            groups (list): The list of groups to process.

        Returns:
            list: A list of groups including associations
        """
        data = []
        # process group objects
        for xid in groups.keys():
            # get association from group data
            assoc_group_data = self.data_group_association(xid)
            data += assoc_group_data
            entity_count += len(assoc_group_data)

            if entity_count >= self._batch_max_chunk:
                break
        return data, entity_count

    def data_indicators(self, indicators, entity_count):
        """Process Indicator data."""
        data = []
        # process indicator objects
        for xid, indicator_data in indicators.items():
            entity_count += 1
            if isinstance(indicator_data, dict):
                data.append(indicator_data)
            else:
                data.append(indicator_data.data)
            del indicators[xid]
            if entity_count >= self._batch_max_chunk:
                break
        return data, entity_count

    @property
    def debug(self):
        """Return debug setting"""
        debug = False
        if os.path.isfile(os.path.join(self.tcex.args.tc_temp_path, 'DEBUG')):
            debug = True
        return debug

    def document(self, name, file_name, **kwargs):
        """Add Document data to Batch object.

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached file for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                                               file content.
            malware (bool, kwargs): If true the file is considered malware.
            password (bool, kwargs): If malware is true a password for the zip archive is
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Document.
        """
        group_obj = Document(name, file_name, **kwargs)
        return self._group(group_obj)

    def email(self, name, subject, header, body, **kwargs):
        """Add Email data to Batch object.

        Args:
            name (str): The name for this Group.
            subject (str): The subject for this Email.
            header (str): The header for this Email.
            body (str): The body for this Email.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            from_addr (str, kwargs): The **from** address for this Email.
            to_addr (str, kwargs): The **to** address for this Email.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Email.
        """
        group_obj = Email(name, subject, header, body, **kwargs)
        return self._group(group_obj)

    def email_address(self, address, **kwargs):
        """Add Email Address data to Batch object.

        Args:
            address (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of EmailAddress.
        """
        indicator_obj = EmailAddress(address, **kwargs)
        return self._indicator(indicator_obj)

    def event(self, name, **kwargs):
        """Add Event data to Batch object.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Event.
        """
        group_obj = Event(name, **kwargs)
        return self._group(group_obj)

    def file(self, md5=None, sha1=None, sha256=None, **kwargs):
        """Add File data to Batch object.

        .. note:: A least one file hash value must be specified.

        Args:
            md5 (str, optional): The md5 value for this Indicator.
            sha1 (str, optional): The sha1 value for this Indicator.
            sha256 (str, optional): The sha256 value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            size (str, kwargs): The file size for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of File.
        """
        indicator_obj = File(md5, sha1, sha256, **kwargs)
        return self._indicator(indicator_obj)

    @property
    def files(self):
        """Return dictionary containing all of the file content or callbacks."""
        return self._files

    @staticmethod
    def generate_xid(identifier=None):
        """Generate xid from provided identifiers.

        .. Important::  If no identifier is provided a unique xid will be returned, but it will
                        not be reproducible. If a list of identifiers are provided they must be
                        in the same order to generate a reproducible xid.

        Args:
            identifier (list|str):  Optional *string* value(s) to be used to make a unique and
                                    reproducible xid.

        """
        if identifier is None:
            identifier = str(uuid.uuid4())
        elif isinstance(identifier, list):
            identifier = '-'.join([str(i) for i in identifier])
            identifier = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
        return hashlib.sha256(identifier.encode('utf-8')).hexdigest()

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
        group_obj = Group(group_type, name, **kwargs)
        return self._group(group_obj)

    @property
    def group_shelf_fqfn(self):
        """Return groups shelf fully qualified filename.

        For testing/debugging a previous shelf file can be copied into the tc_temp_path directory
        instead of creating a new shelf file.
        """
        if self._group_shelf_fqfn is None:
            # new shelf file
            self._group_shelf_fqfn = os.path.join(
                self.tcex.args.tc_temp_path, 'groups-{}'.format(str(uuid.uuid4()))
            )

            # saved shelf file
            if self.stored_groups:
                self._group_shelf_fqfn = os.path.join(self.tcex.args.tc_temp_path, 'groups-saved')
        return self._group_shelf_fqfn

    @property
    def group_types(self):
        """All supported ThreatConnect Group types."""
        return {
            'Adversary': {'apiBranch': 'adversaries', 'apiEntity': 'adversary'},
            'Campaign': {'apiBranch': 'campaigns', 'apiEntity': 'campaign'},
            'Document': {'apiBranch': 'documents', 'apiEntity': 'document'},
            'Emails': {'apiBranch': 'emails', 'apiEntity': 'email'},
            'Event': {'apiBranch': 'events', 'apiEntity': 'event'},
            'Incident': {'apiBranch': 'incidents', 'apiEntity': 'incident'},
            'Intrusion Set': {'apiBranch': 'intrusionSets', 'apiEntity': 'intrusionSet'},
            'Report': {'apiBranch': 'reports', 'apiEntity': 'report'},
            'Signature': {'apiBranch': 'signatures', 'apiEntity': 'signature'},
            'Threat': {'apiBranch': 'threats', 'apiEntity': 'threat'},
        }

    @property
    def groups(self):
        """Return dictionary of all Groups data."""
        if self._groups is None:
            # plain dict, but could be something else in future
            self._groups = {}
        return self._groups

    @property
    def groups_shelf(self):
        """Return dictionary of all Groups data."""
        if self._groups_shelf is None:
            self._groups_shelf = shelve.open(self.group_shelf_fqfn, writeback=False)
        return self._groups_shelf

    def host(self, hostname, **kwargs):
        """Add Email Address data to Batch object.

        Args:
            hostname (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            dns_active (bool, kwargs): When True, DNS active is enabled for this indicator.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            whois_active (bool, kwargs): When True, WhoIs active is enabled for this indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of Host.
        """
        indicator_obj = Host(hostname, **kwargs)
        return self._indicator(indicator_obj)

    def incident(self, name, **kwargs):
        """Add Incident data to Batch object.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Incident.
        """
        group_obj = Incident(name, **kwargs)
        return self._group(group_obj)

    def indicator(self, indicator_type, summary, **kwargs):
        """Add Indicator data to Batch object.

        Args:
            indicator_type (str): The ThreatConnect define Indicator type.
            summary (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of Indicator.
        """
        indicator_obj = Indicator(indicator_type, summary, **kwargs)
        return self._indicator(indicator_obj)

    @property
    def indicator_shelf_fqfn(self):
        """Return indicator shelf fully qualified filename.

        For testing/debugging a previous shelf file can be copied into the tc_temp_path directory
        instead of creating a new shelf file.
        """
        if self._indicator_shelf_fqfn is None:
            # new shelf file
            self._indicator_shelf_fqfn = os.path.join(
                self.tcex.args.tc_temp_path, 'indicators-{}'.format(str(uuid.uuid4()))
            )

            # saved shelf file
            if self.stored_indicators:
                self._indicator_shelf_fqfn = os.path.join(
                    self.tcex.args.tc_temp_path, 'indicators-saved'
                )
        return self._indicator_shelf_fqfn

    @property
    def indicators(self):
        """Return dictionary of all Indicator data."""
        if self._indicators is None:
            # plain dict, but could be something else in future
            self._indicators = {}
        return self._indicators

    @property
    def indicators_shelf(self):
        """Return dictionary of all Indicator data."""
        if self._indicators_shelf is None:
            self._indicators_shelf = shelve.open(self.indicator_shelf_fqfn, writeback=False)
        return self._indicators_shelf

    def intrusion_set(self, name, **kwargs):
        """Add Intrusion Set data to Batch object.

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of IntrusionSet.
        """
        group_obj = IntrusionSet(name, **kwargs)
        return self._group(group_obj)

    def mutex(self, mutex, **kwargs):
        """Add Mutex data to Batch object.

        Args:
            mutex (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of Mutex.
        """
        indicator_obj = Mutex(mutex, **kwargs)
        return self._indicator(indicator_obj)

    def registry_key(self, key_name, value_name, value_type, **kwargs):
        """Add Registry Key data to Batch object.

        Args:
            key_name (str): The key_name value for this Indicator.
            value_name (str): The value_name value for this Indicator.
            value_type (str): The value_type value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of Registry Key.
        """
        indicator_obj = RegistryKey(key_name, value_name, value_type, **kwargs)
        return self._indicator(indicator_obj)

    def report(self, name, **kwargs):
        """Add Report data to Batch object.

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached file for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                file content.
            publish_date (str, kwargs): The publish datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Report.
        """
        group_obj = Report(name, **kwargs)
        return self._group(group_obj)

    def save(self, resource):
        """Wrapper for store method."""
        self.store(resource)

    def store(self, resource):
        """Store group|indicator dict or object to shelve.

        Best effort to save group/indicator data to disk.  If for any reason the save fails
        the data will still be accessible from list in memory.

        Args:
            resource (dict|obj): The Group or Indicator dict or object.
        """
        resource_type = None
        xid = None
        if isinstance(resource, dict):
            resource_type = resource.get('type')
            xid = resource.get('xid')
        else:
            resource_type = resource.type
            xid = resource.xid

        if resource_type is not None and xid is not None:
            saved = True
            if resource_type in self.tcex.group_types:
                try:
                    # groups
                    self.groups_shelf[xid] = resource
                except Exception:
                    saved = False

                if saved:
                    try:
                        del self._groups[xid]
                    except KeyError:
                        # if group was saved twice it would already be delete
                        pass
            elif resource_type in self.tcex.indicator_types_data.keys():
                try:
                    # indicators
                    self.indicators_shelf[xid] = resource
                except Exception:
                    saved = False

                if saved:
                    try:
                        del self._indicators[xid]
                    except KeyError:
                        # if indicator was saved twice it would already be delete
                        pass

    @property
    def stored_groups(self):
        """Return True if saved group files exits, else False."""
        if self._stored_groups is None:
            self._stored_groups = False
            fqfn_saved = os.path.join(self.tcex.args.tc_temp_path, 'groups-saved')
            if (
                self.enable_saved_file
                and os.path.isfile(fqfn_saved)
                and os.access(fqfn_saved, os.R_OK)
            ):
                self._stored_groups = True
                self.tcex.log.debug('groups-saved file found')
        return self._stored_groups

    @property
    def stored_indicators(self):
        """Return True if saved indicators files exits, else False."""
        if self._stored_indicators is None:
            self._stored_indicators = False
            fqfn_saved = os.path.join(self.tcex.args.tc_temp_path, 'indicators-saved')
            if (
                self.enable_saved_file
                and os.path.isfile(fqfn_saved)
                and os.access(fqfn_saved, os.R_OK)
            ):
                self._stored_indicators = True
                self.tcex.log.debug('indicators-saved file found')
        return self._stored_indicators

    @property
    def saved_xids(self):
        """Return previously saved xids."""
        if self._saved_xids is None:
            self._saved_xids = []
            if self.debug:
                fpfn = os.path.join(self.tcex.args.tc_temp_path, 'xids-saved')
                if os.path.isfile(fpfn) and os.access(fpfn, os.R_OK):
                    with open(fpfn) as fh:
                        self._saved_xids = fh.read().splitlines()
        return self._saved_xids

    def signature(self, name, file_name, file_type, file_text, **kwargs):
        """Add Signature data to Batch object.

        Valid file_types:
        + Snort ®
        + Suricata
        + YARA
        + ClamAV ®
        + OpenIOC
        + CybOX ™
        + Bro
        + Regex
        + SPL - Splunk ® Search Processing Language

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached signature for this Group.
            file_type (str): The signature type for this Group.
            file_text (str): The signature content for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Signature.
        """
        group_obj = Signature(name, file_name, file_type, file_text, **kwargs)
        return self._group(group_obj)

    def threat(self, name, **kwargs):
        """Add Threat data to Batch object

        Args:
            name (str): The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.

        Returns:
            obj: An instance of Threat.
        """
        group_obj = Threat(name, **kwargs)
        return self._group(group_obj)

    def user_agent(self, text, **kwargs):
        """Add User Agent data to Batch object

        Args:
            text (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            obj: An instance of UserAgent.
        """
        indicator_obj = UserAgent(text, **kwargs)
        return self._indicator(indicator_obj)

    def url(self, text, **kwargs):
        """Add URL Address data to Batch object.

        Args:
            text (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.

        Returns:
            tcex.tcex_ti.URL: An instance of URL object.
        """
        indicator_obj = URL(text, **kwargs)
        return self._indicator(indicator_obj)

    def write_batch_json(self, content):
        """Write batch json data to a file."""
        # TODO: BCS - rename this method to write data so v2 can use it.
        timestamp = str(time.time()).replace('.', '')
        batch_json_file = os.path.join(
            self.tcex.args.tc_temp_path, 'batch-{}.json'.format(timestamp)
        )
        with open(batch_json_file, 'w') as fh:
            json.dump(content, fh, indent=2)

    @property
    def v2(self):
        """Instance of BatchSubmit"""
        if self._v2 is None:
            self._v2 = TiV2Create(self)
        return self._v2

    @property
    def file_len(self):
        """Return the number of current indicators."""
        return len(self._files)

    @property
    def group_len(self):
        """Return the number of current groups."""
        return len(self.groups) + len(self.groups_shelf)

    @property
    def indicator_len(self):
        """Return the number of current indicators."""
        return len(self.indicators) + len(self.indicators_shelf)

    def __len__(self):
        """Return the number of groups and indicators."""
        return self.group_len + self.indicator_len

    def __str__(self):
        """Return string represtentation of object."""
        groups = []
        for group_data in self.groups.values():
            if isinstance(group_data, dict):
                groups.append(group_data)
            else:
                groups.append(group_data.data)
        for group_data in self.groups_shelf.values():
            if isinstance(group_data, dict):
                groups.append(group_data)
            else:
                groups.append(group_data.data)

        indicators = []
        for indicator_data in self.indicators.values():
            if isinstance(indicator_data, dict):
                indicators.append(indicator_data)
            else:
                indicators.append(indicator_data.data)
        for indicator_data in self.indicators_shelf.values():
            if isinstance(indicator_data, dict):
                indicators.append(indicator_data)
            else:
                indicators.append(indicator_data.data)

        data = {'group': groups, 'indicators': indicators}
        return json.dumps(data, indent=4, sort_keys=True)


class TiCreate(object):
    """Submit Threat Intelligence using ThreatConnect API."""

    def __init__(self, ti):
        """Initialize class properties.

        Args:
            tcex (tcex.tcex.TcEx): Instance of tcex.
        """
        self.ti = ti
        self.tcex = ti.tcex
        self._halt_on_file_error = True

    @property
    def halt_on_file_error(self):
        """Return halt on file post error value."""
        return self._halt_on_file_error

    @halt_on_file_error.setter
    def halt_on_file_error(self, value):
        """Set halt on file post error value."""
        if isinstance(value, bool):
            self._halt_on_file_error = value

    def submit_files(self, owner, halt_on_error=True):
        """Submit Files for Documents and Reports to ThreatConnect API.

        Args:
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            dict: The upload status for each xid.
        """
        # check global setting for override
        if self.halt_on_file_error is not None:
            halt_on_error = self.halt_on_file_error

        upload_status = []
        # TODO: changing dictionary during iteration?
        for xid, content_data in self.ti._files.items():
            del self.ti._files[xid]  # win or loose remove the entry
            status = True

            # used for debug/testing to prevent upload of previously uploaded file
            if self.ti.debug and xid in self.ti.saved_xids:
                self.tcex.log.debug('skipping previously saved file {}.'.format(xid))
                continue

            # process the file content
            content = content_data.get('fileContent')
            if callable(content):
                content = content_data.get('fileContent')(xid)
            if content is None:
                upload_status.append({'uploaded': False, 'xid': xid})
                self.tcex.log.warning('File content was null for xid {}.'.format(xid))
                continue
            if content_data.get('type') == 'Document':
                api_branch = 'documents'
            elif content_data.get('type') == 'Report':
                api_branch = 'reports'

            # Post File
            url = '/v2/groups/{}/{}/upload'.format(api_branch, xid)
            headers = {'Content-Type': 'application/octet-stream'}
            params = {'owner': owner}
            r = self.submit_file_content('POST', url, content, headers, params, halt_on_error)
            if r.status_code == 401:
                # use PUT method if file already exists
                self.tcex.log.info('Received 401 status code using POST. Trying PUT to update.')
                r = self.submit_file_content('PUT', url, content, headers, params, halt_on_error)
            self.tcex.log.debug('{} Upload URL: {}.'.format(content_data.get('type'), r.url))
            if not r.ok:
                status = False
                self.tcex.handle_error(585, [r.status_code, r.text], halt_on_error)
            # TODO: BCS - where do we get debug and saved xids
            elif self.ti.debug:
                self.ti.saved_xids.append(xid)
            self.tcex.log.info('Status {} for file upload with xid {}.'.format(r.status_code, xid))
            upload_status.append({'uploaded': status, 'xid': xid})
        return upload_status

    def submit_file_content(self, method, url, data, headers, params, halt_on_error=True):
        """Submit File Content for Documents and Reports to ThreatConnect API.

        Args:
            method (str): The HTTP method for the request (POST, PUT).
            url (str): The URL for the request.
            data (str;bytes;file): The body (data) for the request.
            headers (dict): The headers for the request.
            params (dict): The query string parameters for the request.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            requests.models.Response: The response from the request.
        """
        r = None
        try:
            r = self.tcex.session.request(method, url, data=data, headers=headers, params=params)
        except Exception as e:
            self.tcex.handle_error(580, [e], halt_on_error)
        return r


class TiBatchCreate(TiCreate):
    """Submit Threat Intelligence using ThreatConnect Batch API endpoint."""

    def __init__(
        self,
        ti,
        action=None,
        attribute_write_type=None,
        halt_on_error=True,
        playbook_triggers_enabled=False,
    ):
        """Initialize class properties.

        Args:
            ti (tcex.tcex.TcExTi): Instance of TcExTi class.
            action (str, optional): Defaults to Create. The action to perform on the TI Data.
                Supported values are Create or Delete.
            attribute_write_type (str, optional): Defaults to Replace. The write type for
                attributes on the TI data.  Supported options is currently only Replace.
            halt_on_error (bool, optional): Defaults to True. Indicates whether the batch job
                should halt processing if there are errors during ingest of the TI.
            playbook_triggers_enabled (bool, optional): Defaults to False. Controls whether
                playbooks should be triggered on TI creation.
        """

        super(TiBatchCreate, self).__init__(ti)
        self._action = action or 'Create'
        self._attribute_write_type = attribute_write_type or 'Replace'
        self._batch_max_chunk = 5000
        self._halt_on_error = halt_on_error
        # TODO: fix these two variables
        self._halt_on_batch_error = True
        self._halt_on_poll_error = True
        self._playbook_triggers_enabled = playbook_triggers_enabled

        # default properties
        self._batch_data_count = None
        self._poll_interval = None
        self._poll_interval_times = []
        self._poll_timeout = 3600

    @property
    def _critical_failures(self):
        """Critical errors returned by ThreatConnect Batch API."""
        return [
            'Encountered an unexpected Exception while processing batch job',
            'would exceed the number of allowed indicators',
        ]

    @property
    def action(self):
        """Return batch action."""
        return self._action

    @action.setter
    def action(self, action):
        """Set batch action."""
        self._action = action

    @property
    def attribute_write_type(self):
        """Return batch attribute write type."""
        return self._attribute_write_type

    @attribute_write_type.setter
    def attribute_write_type(self, attribute_write_type):
        """Set batch attribute write type."""
        self._attribute_write_type = attribute_write_type

    def errors(self, batch_id, halt_on_error=True):
        """Retrieve Batch errors to ThreatConnect API.

        .. code-block:: javascript

            [{
                "errorReason": "Incident incident-001 has an invalid status.",
                "errorSource": "incident-001 is not valid."
            }, {
                "errorReason": "Incident incident-002 has an invalid status.",
                "errorSource":"incident-002 is not valid."
            }]

        Args:
            batch_id (str): The Id returned from the ThreatConnect API for the current batch job.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            list: A list of dictionaries containing batch error data.
        """

        errors = []
        try:
            r = self.tcex.session.get('/v2/batch/{}/errors'.format(batch_id))
            self.tcex.log.debug(
                'Retrieve Errors for ID {}: status code {}, errors {}'.format(
                    batch_id, r.status_code, r.text
                )
            )
            # API does not return correct content type
            if r.ok:
                errors = json.loads(r.text)
            # temporarily process errors to find "critical" errors.
            # FR in core to return error codes.
            for error in errors:
                error_reason = error.get('errorReason')
                for error_msg in self._critical_failures:
                    if re.findall(error_msg, error_reason):
                        self.tcex.handle_error(1500, [error_reason], halt_on_error)
            return errors
        except Exception as e:
            self.tcex.handle_error(560, [e], halt_on_error)

    @property
    def halt_on_error(self):
        """Return batch halt on error setting."""
        return self._halt_on_error

    @halt_on_error.setter
    def halt_on_error(self, halt_on_error):
        """Set batch halt on error setting."""
        self._halt_on_error = halt_on_error

    @property
    def halt_on_batch_error(self):
        """Return halt on batch error value."""
        return self._halt_on_batch_error

    @halt_on_batch_error.setter
    def halt_on_batch_error(self, value):
        """Set batch halt on batch error value."""
        if isinstance(value, bool):
            self._halt_on_batch_error = value

    @property
    def halt_on_poll_error(self):
        """Return halt on poll error value."""
        return self._halt_on_poll_error

    @halt_on_poll_error.setter
    def halt_on_poll_error(self, value):
        """Set batch halt on poll error value."""
        if isinstance(value, bool):
            self._halt_on_poll_error = value

    @property
    def playbook_triggers_enabled(self):
        """Return playbook_triggers_enabled action."""
        return self._playbook_triggers_enabled

    @playbook_triggers_enabled.setter
    def playbook_triggers_enabled(self, playbook_triggers_enabled):
        """Set batch playbook_triggers_enabled bool value.

        Args:
            playbook_triggers_enabled (bool, optional): Defaults to False. Controls whether
                playbooks should be triggered on TI creation.
        """
        self._playbook_triggers_enabled = playbook_triggers_enabled

    def poll(self, batch_id, retry_seconds=None, back_off=None, timeout=None, halt_on_error=True):
        """Poll Batch status to ThreatConnect API.

        .. code-block:: javascript

            {
                "status": "Success",
                "data": {
                    "batchStatus": {
                        "id":3505,
                        "status":"Completed",
                        "errorCount":0,
                        "successCount":0,
                        "unprocessCount":0
                    }
                }
            }

        Args:
            batch_id (str): The Id returned from the ThreatConnect API for the current batch job.
            retry_seconds (int): The base number of seconds used for retries when job is not
                completed.
            back_off (float, optional): Defaults to None. A multiplier to use for backing off on
                each poll attempt when job has not completed.
            timeout (int, optional): Defaults to None. The number of seconds before the poll should
                timeout.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            dict: The batch status returned from the ThreatConnect API.
        """

        # check global setting for override
        if self.halt_on_poll_error is not None:
            halt_on_error = self.halt_on_poll_error

        # initial poll interval
        # TODO: BCS - WTH
        if self._poll_interval is None and self._batch_data_count is not None:
            # calculate poll_interval base off the number of entries in the batch data
            # with a minimum value of 5 seconds.
            self._poll_interval = max(math.ceil(self._batch_data_count / 300), 5)
        elif self._poll_interval is None:
            # if not able to calculate poll_interval default to 15 seconds
            self._poll_interval = 15

        # poll retry back_off factor
        if back_off is None:
            poll_interval_back_off = 2.5
        else:
            poll_interval_back_off = float(back_off)

        # poll retry seconds
        if retry_seconds is None:
            poll_retry_seconds = 5
        else:
            poll_retry_seconds = int(retry_seconds)

        # poll timeout
        if timeout is None:
            timeout = self.poll_timeout
        else:
            timeout = int(timeout)
        params = {'includeAdditional': 'true'}

        poll_count = 0
        poll_time_total = 0
        data = {}
        while True:
            poll_count += 1
            poll_time_total += self._poll_interval
            time.sleep(self._poll_interval)
            self.tcex.log.info('Batch poll time: {} seconds'.format(poll_time_total))
            try:
                # retrieve job status
                r = self.tcex.session.get('/v2/batch/{}'.format(batch_id), params=params)
                if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                    self.tcex.handle_error(545, [r.status_code, r.text], halt_on_error)
                    return data
                data = r.json()
                if data.get('status') != 'Success':
                    self.tcex.handle_error(545, [r.status_code, r.text], halt_on_error)
            except Exception as e:
                self.tcex.handle_error(540, [e], halt_on_error)

            if data.get('data', {}).get('batchStatus', {}).get('status') == 'Completed':
                # store last 5 poll times to use in calculating average poll time
                modifier = poll_time_total * 0.7
                self._poll_interval_times = self._poll_interval_times[-4:] + [modifier]

                weights = [1]
                poll_interval_time_weighted_sum = 0
                for poll_interval_time in self._poll_interval_times:
                    poll_interval_time_weighted_sum += poll_interval_time * weights[-1]
                    # weights will be [1, 1.5, 2.25, 3.375, 5.0625] for all 5 poll times depending
                    # on how many poll times are available.
                    weights.append(weights[-1] * 1.5)

                # pop off the last weight so its not added in to the sum
                weights.pop()

                # calculate the weighted average of the last 5 poll times
                self._poll_interval = math.floor(poll_interval_time_weighted_sum / sum(weights))

                if poll_count == 1:
                    # if completed on first poll, reduce poll interval.
                    self._poll_interval = self._poll_interval * 0.85

                self.tcex.log.debug('Batch Status: {}'.format(data))
                return data

            # update poll_interval for retry with max poll time of 20 seconds
            self._poll_interval = min(
                poll_retry_seconds + int(poll_count * poll_interval_back_off), 20
            )

            # time out poll to prevent App running indefinitely
            if poll_time_total >= timeout:
                self.tcex.handle_error(550, [timeout], True)

    @property
    def poll_timeout(self):
        """Return current poll timeout value."""
        return self._poll_timeout

    @poll_timeout.setter
    def poll_timeout(self, seconds):
        """Set the poll timeout value."""
        self._poll_timeout = int(seconds)

    def settings(self, owner):
        """Return batch job settings."""
        _settings = {
            'action': self._action,
            'attributeWriteType': self._attribute_write_type,  # "Append" requires TC 5.8
            'haltOnError': str(self._halt_on_error).lower(),
            'owner': owner,
            'version': 'V2',
        }
        if self._playbook_triggers_enabled is not None:
            _settings['playbookTriggersEnabled'] = str(self._playbook_triggers_enabled).lower()
        return _settings

    def submit(self, owner, poll=True, errors=True, process_files=True, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.

        By default this method will submit the job request and data and if the size of the data
        is below the value **synchronousBatchSaveLimit** set in System Setting it will process
        the request synchronously and return the batch status.  If the size of the batch is greater
        than the value set the batch job will be queued.
        Errors are not retrieve automatically and need to be enabled.

        If any of the submit, poll, or error methods fail the entire submit will halt at the point
        of failure. The behavior can be changed by setting halt_on_error to False.

        Each of these methods can also be called on their own for greater control of the submit
        process.

        Args:
            batch_data (dict): The batch data to submit to ThreatConnect.
            owner (str): The ThreatConnect owner used for writing the TI data.
            poll (bool, optional): Defaults to True. When True, the status of the batch job will
                checked by polling the ThreatConnect API until completed or the poll timeouts.
            errors (bool, optional): Defaults to True. When True and poll is True, automatically
                retrieve any batch errors.
            process_files (bool, optional): Defaults to True. When True, send any document or report
                attachments to the API.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """

        batch_data = (
            self.submit_create_and_upload(owner, halt_on_error)
            .get('data', {})
            .get('batchStatus', {})
        )
        batch_id = batch_data.get('id')
        if batch_id is not None:
            self.tcex.log.info('Batch ID: {}'.format(batch_id))
            # job hit queue
            if poll:
                # poll for status
                batch_data = (
                    self.poll(batch_id, halt_on_error=halt_on_error)
                    .get('data', {})
                    .get('batchStatus')
                )
                if errors:
                    # retrieve errors
                    error_groups = batch_data.get('errorGroupCount', 0)
                    error_indicators = batch_data.get('errorIndicatorCount', 0)
                    if error_groups > 0 or error_indicators > 0:
                        self.tcex.log.debug('retrieving batch errors')
                        batch_data['errors'] = self.errors(batch_id)
            else:
                # when polling is False, disable file processing since batch status is unknown.
                process_files = False

        if process_files:
            # when process_files is True, upload file data to ThreatConnect.
            batch_data['uploadStatus'] = self.submit_files(halt_on_error)
        return batch_data

    def submit_all(self, owner, poll=True, errors=True, process_files=True, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.

        By default this method will submit the job request and submit the batch data. If the size
        of the data is below the value **synchronousBatchSaveLimit** set in System Setting, the
        data will be processed synchronously and return the batch status. If the size of the batch
        data is exceeds the set value, then the batch job will be queued.

        If any of the submit, poll, or error methods fail the entire submit will halt at the point
        of failure. The behavior can be changed by setting halt_on_error to False.

        .. Note:: Each of these methods can also be called on their own for greater control of the
            submit process.

        Args:
            batch_data (dict): The batch data to submit to ThreatConnect.
            owner (str): The ThreatConnect owner used for writing the TI data.
            poll (bool, optional): Defaults to True. When True, the status of the batch job will
                checked by polling the ThreatConnect API until completed or the poll timeouts.
            errors (bool, optional): Defaults to True. When True and poll is True, automatically
                retrieve any batch errors.
            process_files (bool, optional): Defaults to True. When True, send any document or report
                attachments to the API.
            halt_on_error (bool, optional): Defaults to True. Indicates whether the batch job
                should halt processing if there are errors during ingest of the TI.

        Returns:
            dict: The Batch Status from the ThreatConnect API.
        """

        batch_data_array = []
        while True:
            batch_data = {}
            batch_id = None
            if self.action.lower() == 'delete':
                # while waiting of FR for delete support in createAndUpload submit delete request
                # the old way (submit job + submit data), still using V2.
                if len(self) > 0:  # pylint: disable=C1801
                    batch_id = self.submit_job(owner, halt_on_error)
                    if batch_id is not None:
                        batch_data = self.submit_data(owner, batch_id, halt_on_error)
                else:
                    batch_data = {}
            else:
                batch_data = (
                    self.submit_create_and_upload(owner, halt_on_error)
                    .get('data', {})
                    .get('batchStatus', {})
                )
                batch_id = batch_data.get('id')

            if not batch_data:
                break
            elif batch_id is not None:
                self.tcex.log.info('Batch ID: {}'.format(batch_id))
                # job hit queue
                if poll:
                    # poll for status
                    batch_data = (
                        self.poll(batch_id, halt_on_error=halt_on_error)
                        .get('data', {})
                        .get('batchStatus')
                    )
                    if errors:
                        # retrieve errors
                        error_count = batch_data.get('errorCount', 0)
                        error_groups = batch_data.get('errorGroupCount', 0)
                        error_indicators = batch_data.get('errorIndicatorCount', 0)
                        if error_count > 0 or error_groups > 0 or error_indicators > 0:
                            self.tcex.log.debug('retrieving batch errors')
                            batch_data['errors'] = self.errors(batch_id)
                else:
                    # can't process files if status is unknown (polling must be enabled)
                    process_files = False

            if process_files:
                # submit file data after batch job is complete
                batch_data['uploadStatus'] = self.submit_files(owner, halt_on_error)
            batch_data_array.append(batch_data)
        return batch_data_array

    def submit_create_and_upload(self, owner, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.

        Args:
            owner (str): The ThreatConnect owner used for writing the TI data.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            dict: The Batch Status from the ThreatConnect API.
        """

        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        content = self.ti.data
        # store the length of the batch data to use for poll interval calculations
        self.tcex.log.info('Batch Group Size: {:,}.'.format(len(content.get('group'))))
        self.tcex.log.info('Batch Indicator Size {:,}.'.format(len(content.get('indicator'))))
        # TODO: is this still needed?
        # if self.debug:
        #     # special code for debugging App using batchV2.
        #     self.write_batch_json(content)
        if content.get('group') or content.get('indicator'):
            try:
                files = (
                    ('config', json.dumps(self.settings(owner))),
                    ('content', json.dumps(content)),
                )
                params = {'includeAdditional': 'true'}
                r = self.tcex.session.post('/v2/batch/createAndUpload', files=files, params=params)
                self.tcex.log.debug('Batch Status Code: {}'.format(r.status_code))
            except Exception as e:
                self.tcex.handle_error(1505, [e], halt_on_error)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.tcex.handle_error(1510, [r.status_code, r.text], halt_on_error)
            return r.json()
        return {}

    def submit_data(self, owner, batch_id, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.

        Args:
            owner (str): The ThreatConnect owner used for writing the TI data.
            batch_id (str): The Id returned from the ThreatConnect API for the current batch job.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            dict: The response from the Batch API call.
        """
        print('owner', owner)

        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        content = self.ti.data
        # store the length of the batch data to use for poll interval calculations
        self._batch_data_count = len(content.get('group')) + len(content.get('indicator'))
        self.tcex.log.info('Batch Size: {:,}'.format(self._batch_data_count))
        if content.get('group') or content.get('indicator'):
            headers = {'Content-Type': 'application/octet-stream'}
            try:
                r = self.tcex.session.post(
                    '/v2/batch/{}'.format(batch_id), headers=headers, json=content
                )
            except Exception as e:
                self.tcex.handle_error(1520, [e], halt_on_error)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.tcex.handle_error(1525, [r.status_code, r.text], halt_on_error)
            return r.json()
        return {}

    def submit_job(self, owner, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.

        Args:
            owner (str): The ThreatConnect owner used for writing the TI data.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            str: The Id returned from the ThreatConnect API for the current batch job.
        """

        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        try:
            r = self.tcex.session.post('/v2/batch', json=self.settings(owner))
        except Exception as e:
            self.tcex.handle_error(1505, [e], halt_on_error)
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.tcex.handle_error(1510, [r.status_code, r.text], halt_on_error)
        data = r.json()
        if data.get('status') != 'Success':
            self.tcex.handle_error(1510, [r.status_code, r.text], halt_on_error)
        self.tcex.log.debug('Batch Submit Data: {}'.format(data))
        return data.get('data', {}).get('batchId')


class TiV2Create(TiCreate):
    """Batch Submit Threat Intelligence using ThreatConnect V2 API endpoints."""

    # def __init__(self, ti):
    #     """Initialize class properties.

    #     Args:
    #         ti (tcex.tcex.TcExTi): Instance of TcExTi class.
    #     """
    #     super(TiV2Create, self).__init__(ti)

    def submit(self, owner, halt_on_error=True):
        """Submit Threat Intelligence request to ThreatConnect V2 API.

        Args:
            owner (str): The ThreatConnect owner used for writing the TI data.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            dict: The response data from the ThreatConnect API.
        """

        while True:
            content = self.ti.data
            self.tcex.log.info('Batch Group Size: {:,}.'.format(len(content.get('group'))))
            self.tcex.log.info('Batch Indicator Size {:,}.'.format(len(content.get('indicator'))))

            api_response_data = []
            for group_data in content.get('group', []):
                # add the group
                group_response = self.group_add(owner, group_data, halt_on_error)
                api_response_data.append(group_response.json())

            # for indicator_data in content.get('indicator', []):
            #     pass

            if not content.get('group') and not content.get('indicator'):
                break  # no more groups or indicators to process

    def group_add(self, owner, group_data, halt_on_error=False):
        """Add/update a group to ThreatConnect.

        **API Response:**

        .. code-block:: javascript

            {
              "status": "Success",
              "data": {
                "adversary": {
                  "id": 1,
                  "name": "adversary-001",
                  "owner": {
                    "id": 2,
                    "name": "TCI",
                    "type": "Organization"
                  },
                  "dateAdded": "2019-01-19T21:22:51Z",
                  "webLink": "https://app2.tci.ninja/auth/adversary/adversary.xhtml?adversary=1"
                }
              }
            }

        Args:
            owner ([type]): [description]
            group_data ([type]): [description]
            halt_on_error (bool, optional): Defaults to False. [description]

        Returns:
            [type]: [description]
        """

        # parse group data
        group_id = group_data.pop('id')
        group_name = group_data.get('name')
        group_type = group_data.pop('type')
        group_type_data = self.ti.group_types.get(group_type)

        # extract metadata
        # TODO: handle associations and xid/id map
        # associations = group_data.pop('associatedGroupXid', [])
        attributes = group_data.pop('attribute', [])
        labels = group_data.pop('securityLabel', [])
        tags = group_data.pop('tag', [])
        # xid = group_data.pop('xid')

        if group_id is not None:
            group_params = {}
            group_url = '/v2/groups/{}/{}'.format(group_type_data.get('apiBranch'), group_id)
            r = self.tcex.session.put(group_url, json=group_data, params=group_params)
        else:
            group_params = {'owner': owner}
            group_url = '/v2/groups/{}'.format(group_type_data.get('apiBranch'))
            r = self.tcex.session.post(group_url, json=group_data, params=group_params)

        error_data = [group_type, group_name, r.text or r.reason]
        if self.api_status(r, 605, error_data, halt_on_error):
            group_id = r.json().get('data', {}).get(group_type_data.get('apiEntity'), {}).get('id')
            self.group_add_attributes(group_type, group_id, attributes, halt_on_error)
            self.group_add_labels(group_type, group_id, labels, halt_on_error)
            self.group_add_tags(group_type, group_id, tags, halt_on_error)

        return r

    def group_add_association(self, group_type, group_id, attributes, halt_on_error):
        """Add association to group.

        NOTE: It's better to hold on to group associations until the end to ensure
        that the group has been created before trying to associate.

        """

    def group_add_attributes(self, group_type, group_id, attributes, halt_on_error):
        """Add attribute(s) to a group.

        **API Response:**

        .. code-block:: javascript

            {
                "status": "Success",
                "data": {
                    "attribute": {
                        "id": 1,
                        "type": "Description",
                        "value": "Test Description",
                        "dateAdded": "2019-01-19T21:24:35Z",
                        "lastModified": "2019-01-19T21:24:35Z",
                        "displayed": false
                    }
                }
            }

        Args:
            group_type (str): The group type (e.g., Adversary).
            group_id (int): The ID for the group.
            attributes (list): A list of attributes to add to the Group.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            list: A list of responses from ThreatConnect API for the attribute add.
        """
        api_response_data = []
        for attribute in attributes:
            labels = attribute.pop('securityLabel', [])
            self.tcex.log.debug(
                'Adding attribute type "{}" to Group ID {}'.format(attribute.get('type'), group_id)
            )
            group_type_data = self.ti.group_types.get(group_type)
            group_url = '/v2/groups/{}/{}/attributes'.format(
                group_type_data.get('apiBranch'), group_id
            )
            r = self.tcex.session.post(group_url, json=attribute)

            error_data = [
                attribute.get('type'),
                attribute.get('value'),
                group_id,
                r.text or r.reason,
            ]
            if self.api_status(r, 605, error_data, halt_on_error):
                attribute_id = r.json().get('data', {}).get('id')
                self.group_add_attribute_labels(
                    group_type, group_id, attribute_id, labels, halt_on_error
                )
                # store response
                api_response_data.append(r.json())
        return api_response_data

    def group_add_attribute_labels(
        self, group_type, group_id, attribute_id, labels, halt_on_error=False
    ):
        """Add security label(s) to an attribute.

        /v2/groups/{groupType}/{groupId}/attributes/{attributeId}/securityLabels/{securityLabelName}

        .. code-block:: javascript

            {
                "status": "Success"
            }

        Args:
            group_type (str): The group type (e.g., Adversary).
            group_id (int): The ID for the group.
            attribute_id (int): The ID for the attribute.
            labels (list): A list of security labels to add to the Group.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.
        """
        api_response_data = []
        for label in labels:
            self.tcex.log.debug(
                'Adding label "{}" to Attribute ID {}.'.format(label.get('name'), attribute_id)
            )
            group_type_data = self.ti.group_types.get(group_type)
            group_attribute_label_url = '/v2/groups/{}/{}/attributes/{}/label/{}'.format(
                group_type_data.get('apiBranch'), group_id, attribute_id, quote(label.get('name'))
            )
            r = self.tcex.session.post(group_attribute_label_url)

            error_data = [label, attribute_id, r.text or r.reason]
            api_response_data.append(
                {
                    'label': label.get('name'),
                    'success': self.api_status(r, 650, error_data, halt_on_error),
                }
            )
        return api_response_data

    def group_add_labels(self, group_type, group_id, labels, halt_on_error=True):
        """Add security label(s) to a group.

        /v2/groups/{groupType}/{uniqueId}/securityLabels/{securityLabelName}

        .. code-block:: javascript

            {
                "status": "Success"
            }

        Args:
            group_type (str): The group type (e.g., Adversary).
            group_id (int): The ID for the group.
            labels (list): A list of security labels to add to the Group.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.
        """
        api_response_data = []
        for label in labels:
            self.tcex.log.debug(
                'Adding label "{}" to Group ID {}.'.format(label.get('name'), group_id)
            )
            group_type_data = self.ti.group_types.get(group_type)
            group_label_url = '/v2/groups/{}/{}/label/{}'.format(
                group_type_data.get('apiBranch'), group_id, quote(label.get('name'))
            )
            r = self.tcex.session.post(group_label_url)

            error_data = [label, group_id, r.text or r.reason]
            api_response_data.append(
                {
                    'label': label.get('name'),
                    'success': self.api_status(r, 610, error_data, halt_on_error),
                }
            )
        return api_response_data

    def group_add_tags(self, group_type, group_id, tags, halt_on_error=True):
        """Add tag(s) to group.

        /v2/groups/reports/{uniqueId}/tags/{tagName}

        .. code-block:: javascript

            {
                "status": "Success"
            }

        Args:
            group_type (str): The group type (e.g., Adversary).
            group_id (int): The ID for the group.
            tags (list): A list of tags to add to the Group.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.
        """
        api_response_data = []
        for tag in tags:
            self.tcex.log.debug('Adding tag "{}" to Group ID {}.'.format(tag.get('name'), group_id))
            group_type_data = self.ti.group_types.get(group_type)
            group_tag_url = '/v2/groups/{}/{}/tag/{}'.format(
                group_type_data.get('apiBranch'), group_id, quote(tag.get('name'))
            )
            r = self.tcex.session.post(group_tag_url)

            error_data = [tag, group_id, r.text or r.reason]
            api_response_data.append(
                {
                    'tag': tag.get('name'),
                    'success': self.api_status(r, 615, error_data, halt_on_error),
                }
            )
        return api_response_data

    def api_status(self, r, error_code, error_data, halt_on_error=True):
        """Check API response status and handle any errors.

        Args:
            r (): Requests module response object.
            error_code (int): The error code as defined in tcex_error_codes.
            error_data (list): A list of values to populate error text.
            halt_on_error (bool, optional): Defaults to True. When True, any error will raise
                an exception.

        Returns:
            bool: When True, no errors were encountered with the response.
        """
        status = True
        if r.ok:
            try:
                if r.json().get('status') != 'Success':
                    self.tcex.handle_error(error_code, error_data, halt_on_error)
                    status = False
            except Exception:
                self.tcex.handle_error(error_code, error_data, halt_on_error)
                status = False
        else:
            self.tcex.handle_error(error_code, error_data, halt_on_error)
            status = False
        return status
