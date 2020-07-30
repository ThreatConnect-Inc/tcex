# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module."""
# standard library
import hashlib
import json
import math
import os
import re
import shelve
import time
import uuid
from typing import Optional

from .group import (
    Adversary,
    Campaign,
    Document,
    Email,
    Event,
    Group,
    Incident,
    IntrusionSet,
    Report,
    Signature,
    Threat,
)
from .indicator import (
    ASN,
    CIDR,
    URL,
    Address,
    EmailAddress,
    File,
    Host,
    Indicator,
    Mutex,
    RegistryKey,
    UserAgent,
    custom_indicator_class_factory,
)

# import local modules for dynamic reference
module = __import__(__name__)


class Batch:
    """ThreatConnect Batch Import Module

    Args:
        tcex (obj): An instance of TcEx object.
        owner (str): The ThreatConnect owner for Batch action.
        action (str, default:Create): Action for the batch job ['Create', 'Delete'].
        attribute_write_type (str, default:Replace): Write type for Indicator attributes
            ['Append', 'Replace'].
        halt_on_error (bool, default:True): If True any batch error will halt the batch job.
    """

    def __init__(
        self,
        tcex,
        owner,
        action=None,
        attribute_write_type=None,
        halt_on_error=True,
        playbook_triggers_enabled=None,
    ):
        """Initialize Class properties."""
        self.tcex = tcex
        self._action = action or 'Create'
        self._attribute_write_type = attribute_write_type or 'Replace'
        self._batch_max_chunk = 5000
        self._halt_on_error = halt_on_error
        self._hash_collision_mode = None
        self._file_merge_mode = None
        self._owner = owner
        self._playbook_triggers_enabled = playbook_triggers_enabled

        # shelf settings
        self._group_shelf_fqfn = None
        self._indicator_shelf_fqfn = None

        # global overrides on batch/file errors
        self._halt_on_batch_error = None
        self._halt_on_file_error = None
        self._halt_on_poll_error = None

        # debug/saved flags
        self._saved_xids = None
        self._saved_groups = None  # indicates groups shelf file was provided
        self._saved_indicators = None  # indicates indicators shelf file was provided
        self.enable_saved_file = False

        # default properties
        self._batch_data_count = None
        self._poll_interval = None
        self._poll_interval_times = []
        self._poll_timeout = 3600

        # containers
        self._files = {}
        self._groups = None
        self._groups_shelf = None
        self._indicators = None
        self._indicators_shelf = None

        # build custom indicator classes
        self._gen_indicator_class()

    @property
    def _critical_failures(self):  # pragma: no cover
        """Return Batch critical failure messages."""
        return [
            'Encountered an unexpected Exception while processing batch job',
            'would exceed the number of allowed indicators',
        ]

    def _gen_indicator_class(self):  # pragma: no cover
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

    def _gen_indicator_method(self, name, custom_class, value_count):  # pragma: no cover
        """Dynamically generate custom Indicator methods.

        Args:
            name (str): The name of the method.
            custom_class (object): The class to add.
            value_count (int): The number of value parameters to support.
        """
        method_name = name.replace(' ', '_').lower()

        # Add Method for each Custom Indicator class
        def method_1(value1, xid, **kwargs):  # pylint: disable=possibly-unused-variable
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, xid, **kwargs)
            return self._indicator(indicator_obj)

        def method_2(value1, value2, xid, **kwargs):  # pylint: disable=possibly-unused-variable
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, value2, xid, **kwargs)
            return self._indicator(indicator_obj)

        def method_3(
            value1, value2, value3, xid, **kwargs
        ):  # pylint: disable=possibly-unused-variable
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, value2, value3, xid, **kwargs)
            return self._indicator(indicator_obj)

        method = locals()[f'method_{value_count}']
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

    @property
    def action(self):
        """Return batch action."""
        return self._action

    @action.setter
    def action(self, action):
        """Set batch action."""
        self._action = action

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
                indicator_data[f'value{index}'] = value
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
    def attribute_write_type(self):
        """Return batch attribute write type."""
        return self._attribute_write_type

    @attribute_write_type.setter
    def attribute_write_type(self, attribute_write_type):
        """Set batch attribute write type."""
        self._attribute_write_type = attribute_write_type

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
                    fh.write(f'{xid}\n')
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
        """Return group dict array following all associations.

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
                    'fileName': group_data.get('fileName'),
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
        # we are converting groups.keys() to a list because the data_group_association function
        # will be deleting items the groups dictionary which would raise a
        # "dictionary changed size during iteration" error
        for xid in list(groups.keys()):
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
        for xid, indicator_data in list(indicators.items()):
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

    @property
    def error_codes(self):
        """Return static list of Batch error codes and short description"""
        return {
            '0x1001': 'General Error',
            '0x1002': 'Permission Error',
            '0x1003': 'JsonSyntax Error',
            '0x1004': 'Internal Error',
            '0x1005': 'Invalid Indicator Error',
            '0x1006': 'Invalid Group Error',
            '0x1007': 'Item Not Found Error',
            '0x1008': 'Indicator Limit Error',
            '0x1009': 'Association Error',
            '0x100A': 'Duplicate Item Error',
            '0x100B': 'File IO Error',
            '0x2001': 'Indicator Partial Loss Error',
            '0x2002': 'Group Partial Loss Error',
            '0x2003': 'File Hash Merge Error',
        }

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
            batch_id (str): The ID returned from the ThreatConnect API for the current batch job.
            halt_on_error (bool, default:True): If True any exception will raise an error.
        """
        errors = []
        try:
            r = self.tcex.session.get(f'/v2/batch/{batch_id}/errors')
            # if r.status_code == 404:
            #     time.sleep(5)  # allow time for errors to be processed
            #     r = self.tcex.session.get(f'/v2/batch/{batch_id}/errors')
            self.tcex.log.debug(
                f'Retrieve Errors for ID {batch_id}: status code {r.status_code}, errors {r.text}'
            )
            # self.tcex.log.debug(f'Retrieve Errors URL {r.url}')
            # API does not return correct content type
            if r.ok:
                errors = json.loads(r.text)
            # temporarily process errors to find "critical" errors.
            # FR in core to return error codes.
            for error in errors:
                error_reason = error.get('errorReason')
                for error_msg in self._critical_failures:
                    if re.findall(error_msg, error_reason):
                        self.tcex.handle_error(10500, [error_reason], halt_on_error)
            return errors
        except Exception as e:
            self.tcex.handle_error(560, [e], halt_on_error)

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

    def file_merge_mode(self, value):
        """Set the file merge mode for the entire batch job.

        Args:
            value (str): A value of Distribute or Merge.
        """
        self._file_merge_mode = value

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
                self.tcex.args.tc_temp_path, f'groups-{str(uuid.uuid4())}'
            )

            # saved shelf file
            if self.saved_groups:
                self._group_shelf_fqfn = os.path.join(self.tcex.args.tc_temp_path, 'groups-saved')
        return self._group_shelf_fqfn

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
    def halt_on_file_error(self):
        """Return halt on file post error value."""
        return self._halt_on_file_error

    @halt_on_file_error.setter
    def halt_on_file_error(self, value):
        """Set halt on file post error value."""
        if isinstance(value, bool):
            self._halt_on_file_error = value

    @property
    def halt_on_poll_error(self):
        """Return halt on poll error value."""
        return self._halt_on_poll_error

    @halt_on_poll_error.setter
    def halt_on_poll_error(self, value):
        """Set batch halt on poll error value."""
        if isinstance(value, bool):
            self._halt_on_poll_error = value

    def hash_collision_mode(self, value):
        """Set the file hash collision mode for the entire batch job.

        Args:
            value (str): A value of Split, IgnoreIncoming, IgnoreExisting, FavorIncoming,
                and FavorExisting.
        """
        self._hash_collision_mode = value

    def host(self, hostname, **kwargs):
        """Add Email Address data to Batch object.

        Args:
            hostname (str): The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
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
                self.tcex.args.tc_temp_path, f'indicators-{str(uuid.uuid4())}'
            )

            # saved shelf file
            if self.saved_indicators:
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
            batch_id (str): The ID returned from the ThreatConnect API for the current batch job.
            retry_seconds (int): The base number of seconds used for retries when job is not
                                 completed.
            back_off (float): A multiplier to use for backing off on each poll attempt when job has
                              not completed.
            timeout (int, optional): The number of seconds before the poll should timeout.
            halt_on_error (bool, default:True): If True any exception will raise an error.

        Returns:
            dict: The batch status returned from the ThreatConnect API.
        """
        # check global setting for override
        if self.halt_on_poll_error is not None:
            halt_on_error = self.halt_on_poll_error

        # initial poll interval
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
            self.tcex.log.info(f'Batch poll time: {poll_time_total} seconds')
            try:
                # retrieve job status
                r = self.tcex.session.get(f'/v2/batch/{batch_id}', params=params)
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

                self.tcex.log.debug(f'Batch Status: {data}')
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
        """Save group|indicator dict or object to shelve.

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
    def saved_groups(self):
        """Return True if saved group files exits, else False."""
        if self._saved_groups is None:
            self._saved_groups = False
            fqfn_saved = os.path.join(self.tcex.args.tc_temp_path, 'groups-saved')
            if (
                self.enable_saved_file
                and os.path.isfile(fqfn_saved)
                and os.access(fqfn_saved, os.R_OK)
            ):
                self._saved_groups = True
                self.tcex.log.debug('groups-saved file found')
        return self._saved_groups

    @property
    def saved_indicators(self):
        """Return True if saved indicators files exits, else False."""
        if self._saved_indicators is None:
            self._saved_indicators = False
            fqfn_saved = os.path.join(self.tcex.args.tc_temp_path, 'indicators-saved')
            if (
                self.enable_saved_file
                and os.path.isfile(fqfn_saved)
                and os.access(fqfn_saved, os.R_OK)
            ):
                self._saved_indicators = True
                self.tcex.log.debug('indicators-saved file found')
        return self._saved_indicators

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

    @property
    def settings(self):
        """Return batch job settings."""
        _settings = {
            'action': self._action,
            # not supported in v2 batch
            # 'attributeWriteType': self._attribute_write_type,
            'attributeWriteType': 'Replace',
            'haltOnError': str(self._halt_on_error).lower(),
            'owner': self._owner,
            'version': 'V2',
        }
        if self._playbook_triggers_enabled is not None:
            _settings['playbookTriggersEnabled'] = str(self._playbook_triggers_enabled).lower()
        if self._hash_collision_mode is not None:
            _settings['hashCollisionMode'] = self._hash_collision_mode
        if self._file_merge_mode is not None:
            _settings['fileMergeMode'] = self._file_merge_mode
        return _settings

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

    def submit(self, poll=True, errors=True, process_files=True, halt_on_error=True):
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
            poll (bool, default:True): Poll for status.
            errors (bool, default:True): Retrieve any batch errors (only if poll is True).
            process_files (bool, default:True): Send any document or report attachments to the API.
            halt_on_error (bool, default:True): If True any exception will raise an error.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        batch_data = (
            self.submit_create_and_upload(halt_on_error).get('data', {}).get('batchStatus', {})
        )
        batch_id = batch_data.get('id')
        if batch_id is not None:
            self.tcex.log.info(f'Batch ID: {batch_id}')
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
                # can't process files if status is unknown (polling must be enabled)
                process_files = False

        if process_files:
            # submit file data after batch job is complete
            batch_data['uploadStatus'] = self.submit_files(halt_on_error)
        return batch_data

    def submit_all(self, poll=True, errors=True, process_files=True, halt_on_error=True):
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
            poll (bool, default:True): Poll for status.
            errors (bool, default:True): Retrieve any batch errors (only if poll is True).
            process_files (bool, default:True): Send any document or report attachments to the API.
            halt_on_error (bool, default:True): If True any exception will raise an error.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        batch_data_array = []
        while True:
            batch_data = {}
            batch_id = None
            if self.action.lower() == 'delete':
                # while waiting of FR for delete support in createAndUpload submit delete request
                # the old way (submit job + submit data), still using V2.
                if len(self) > 0:  # pylint: disable=len-as-condition
                    batch_id = self.submit_job(halt_on_error)
                    if batch_id is not None:
                        batch_data = self.submit_data(batch_id, halt_on_error)
                else:
                    batch_data = {}
            else:
                batch_data = (
                    self.submit_create_and_upload(halt_on_error)
                    .get('data', {})
                    .get('batchStatus', {})
                )
                batch_id = batch_data.get('id')

            # break loop when end of data is reached
            if not batch_data:
                break

            if batch_id is not None:
                self.tcex.log.info(f'Batch ID: {batch_id}')
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
                batch_data['uploadStatus'] = self.submit_files(halt_on_error)
            batch_data_array.append(batch_data)

            if self.debug:
                self.write_error_json(batch_data.get('errors'))

        return batch_data_array

    def write_error_json(self, errors: list):
        """Write the errors to a JSON file for debuging purposes.

        Args:
            errors (list): A list of errors to write out.
        """
        if not errors:
            errors = []
        timestamp = str(time.time()).replace('.', '')
        error_json_file = os.path.join(self.tcex.args.tc_temp_path, f'errors-{timestamp}.json')
        with open(error_json_file, 'w') as fh:
            json.dump(errors, fh, indent=2)

    def submit_create_and_upload(self, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        content = self.data
        if content.get('group') or content.get('indicator'):
            if self.debug:
                # special code for debugging App using batchV2.
                self.write_batch_json(content)

            # store the length of the batch data to use for poll interval calculations
            self.tcex.log.info(f"Batch Group Size: {len(content.get('group')):,}.")
            self.tcex.log.info(f"Batch Indicator Size {len(content.get('indicator')):,}.")

            try:
                files = (('config', json.dumps(self.settings)), ('content', json.dumps(content)))
                params = {'includeAdditional': 'true'}
                r = self.tcex.session.post('/v2/batch/createAndUpload', files=files, params=params)
                self.tcex.log.debug(f'Batch Status Code: {r.status_code}')
                if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                    self.tcex.handle_error(10510, [r.status_code, r.text], halt_on_error)
                return r.json()
            except Exception as e:
                self.tcex.handle_error(10505, [e], halt_on_error)
        return {}

    def submit_data(self, batch_id: int, halt_on_error: Optional[bool] = True) -> dict:
        """Submit Batch request to ThreatConnect API.

        Args:
            batch_id (int): The batch id of the current job.
            halt_on_error (Optional[bool] = True): If True the process should halt if any errors
                are encountered.

        Returns:
            dict: The response data
        """

        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        content = self.data
        # store the length of the batch data to use for poll interval calculations
        self._batch_data_count = len(content.get('group')) + len(content.get('indicator'))
        self.tcex.log.info(f'Batch Size: {self._batch_data_count:,}')
        if content.get('group') or content.get('indicator'):
            headers = {'Content-Type': 'application/octet-stream'}
            try:
                r = self.tcex.session.post(f'/v2/batch/{batch_id}', headers=headers, json=content)
                if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                    self.tcex.handle_error(10525, [r.status_code, r.text], halt_on_error)
                return r.json()
            except Exception as e:
                self.tcex.handle_error(10520, [e], halt_on_error)
        return {}

    def submit_files(self, halt_on_error=True):
        """Submit Files for Documents and Reports to ThreatConnect API.

        Critical Errors

        * There is insufficient document storage allocated to this account.

        Args:
            halt_on_error (bool, default:True): If True any exception will raise an error.

        Returns:
            dict: The upload status for each xid.
        """
        # check global setting for override
        if self.halt_on_file_error is not None:
            halt_on_error = self.halt_on_file_error

        upload_status = []
        for xid, content_data in list(self._files.items()):
            del self._files[xid]  # win or loose remove the entry
            status = True

            # used for debug/testing to prevent upload of previously uploaded file
            if self.debug and xid in self.saved_xids:
                self.tcex.log.debug(f'skipping previously saved file {xid}.')
                continue

            # process the file content
            content = content_data.get('fileContent')
            if callable(content):
                content = content_data.get('fileContent')(xid)
            if content is None:
                upload_status.append({'uploaded': False, 'xid': xid})
                self.tcex.log.warning(f'File content was null for xid {xid}.')
                continue
            if content_data.get('type') == 'Document':
                api_branch = 'documents'
            elif content_data.get('type') == 'Report':
                api_branch = 'reports'

            if self.debug and content_data.get('fileName'):
                # special code for debugging App using batchV2.
                fqfn = os.path.join(
                    self.tcex.args.tc_temp_path,
                    f'''{api_branch}--{xid}--{content_data.get('fileName').replace('/', ':')}''',
                )
                with open(fqfn, 'wb') as fh:
                    fh.write(content)

            # Post File
            url = f'/v2/groups/{api_branch}/{xid}/upload'
            headers = {'Content-Type': 'application/octet-stream'}
            params = {'owner': self._owner, 'updateIfExists': 'true'}
            r = self.submit_file_content('POST', url, content, headers, params, halt_on_error)
            if r.status_code == 401:
                # use PUT method if file already exists
                self.tcex.log.info('Received 401 status code using POST. Trying PUT to update.')
                r = self.submit_file_content('PUT', url, content, headers, params, halt_on_error)
            self.tcex.log.debug(f"{content_data.get('type')} Upload URL: {r.url}.")
            if not r.ok:
                status = False
                self.tcex.handle_error(585, [r.status_code, r.text], halt_on_error)
            elif self.debug:
                self.saved_xids.append(xid)
            self.tcex.log.info(f'Status {r.status_code} for file upload with xid {xid}.')
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
            halt_on_error (bool, default:True): If True any exception will raise an error.

        Returns:
            requests.models.Response: The response from the request.
        """
        r = None
        try:
            r = self.tcex.session.request(method, url, data=data, headers=headers, params=params)
        except Exception as e:
            self.tcex.handle_error(580, [e], halt_on_error)
        return r

    def submit_job(self, halt_on_error=True):
        """Submit Batch request to ThreatConnect API."""
        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        try:
            r = self.tcex.session.post('/v2/batch', json=self.settings)
        except Exception as e:
            self.tcex.handle_error(10505, [e], halt_on_error)
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.tcex.handle_error(10510, [r.status_code, r.text], halt_on_error)
        data = r.json()
        if data.get('status') != 'Success':
            self.tcex.handle_error(10510, [r.status_code, r.text], halt_on_error)
        self.tcex.log.debug(f'Batch Submit Data: {data}')
        return data.get('data', {}).get('batchId')

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
            obj: An instance of URL.
        """
        indicator_obj = URL(text, **kwargs)
        return self._indicator(indicator_obj)

    def write_batch_json(self, content):
        """Write batch json data to a file."""
        if content:
            timestamp = str(time.time()).replace('.', '')
            batch_json_file = os.path.join(self.tcex.args.tc_temp_path, f'batch-{timestamp}.json')
            with open(batch_json_file, 'w') as fh:
                json.dump(content, fh, indent=2)

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

    def __str__(self):  # pragma: no cover
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
