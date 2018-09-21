# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""
import hashlib
import json
import math
import os
import re
import shelve
import time
import uuid

from .tcex_utils import TcExUtils

# import local modules for dynamic reference
module = __import__(__name__)


def custom_indicator_class_factory(indicator_type, base_class, class_dict, value_fields):
    """Internal method for dynamically building Custom Indicator Class."""
    value_count = len(value_fields)
    def init_1(self, tcex, value1, rating=None, confidence=None, xid=True):
        """Init method for Custom Indicator Types with one value"""
        summary = self.build_summary(value1)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, rating, confidence, xid)
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_2(self, tcex, value1, value2, rating=None, confidence=None, xid=True):
        """Init method for Custom Indicator Types with two values."""
        summary = self.build_summary(value1, value2)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, rating, confidence, xid)
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_3(self, tcex, value1, value2, value3, rating=None, confidence=None, xid=True):
        """Init method for Custom Indicator Types with three values."""
        summary = self.build_summary(value1, value2, value3)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, rating, confidence, xid)
        for k, v in class_dict.items():
            setattr(self, k, v)

    class_name = indicator_type.replace(' ', '')
    init_method = locals()['init_{}'.format(value_count)]
    newclass = type(str(class_name), (base_class,), {"__init__": init_method})
    return newclass


class TcExBatch(object):
    """ThreatConnect Batch Import Module"""

    def __init__(self, tcex, owner, action=None, attribute_write_type=None, halt_on_error=True):
        """Initialize Class Properties.

        Args:
            tcex (obj): An instance of TcEx object.
            owner (str): The ThreatConnect owner for Batch action.
            action (str, default:Create): Action for the batch job ['Create', 'Delete'].
            attribute_write_type (str, default:Replace): Write type for Indicator attributes
                ['Append', 'Replace'].
            halt_on_error (bool, default:True): If True any batch error will halt the batch job.
        """
        self.tcex = tcex
        self._action = action or 'Create'
        self._attribute_write_type = attribute_write_type or 'Replace'
        self._batch_max_chunk = 5000
        self._halt_on_error = halt_on_error
        self._owner = owner
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
    def _critical_failures(self):
        """Return Batch critical failure messages."""
        return [
            'Encountered an unexpected Exception while processing batch job',
            'would exceed the number of allowed indicators'
        ]

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
        def method_1(value1, rating=None, confidence=None, xid=True):
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, rating, confidence, xid)
            return self._indicator(indicator_obj)

        def method_2(value1, value2, rating=None, confidence=None, xid=True):
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(value1, value2, rating, confidence, xid)
            return self._indicator(indicator_obj)

        def method_3(value1, value2, value3, rating=None, confidence=None, xid=True):
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(
                value1, value2, value3, rating, confidence, xid)
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

    def address(self, ip, rating=None, confidence=None, xid=True):
        """Add Address data to Batch object.

        Args:
            ip (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of Address.
        """
        indicator_obj = Address(ip, rating, confidence, xid)
        return self._indicator(indicator_obj)

    def adversary(self, name, xid=True):
        """Add Adversary data to Batch object.

        Args:
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Adversary.
        """
        group_obj = Adversary(name, xid)
        return self._group(group_obj)

    def asn(self, as_number, rating=None, confidence=None, xid=True):
        """Add ASN data to Batch object.

        Args:
            as_number (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of ASN.
        """
        indicator_obj = ASN(as_number, rating, confidence, xid)
        return self._indicator(indicator_obj)

    @property
    def attribute_write_type(self):
        """Return batch attribute write type."""
        return self._attribute_write_type

    @attribute_write_type.setter
    def attribute_write_type(self, attribute_write_type):
        """Set batch attribute write type."""
        self._attribute_write_type = attribute_write_type

    def campaign(self, name, first_seen=None, xid=True):
        """Add Campaign data to Batch object.

        Args:
            name (str): The name for this Group.
            first_seen (str, optional): The first seen datetime expression for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Campaign.
        """
        group_obj = Campaign(name, first_seen, xid)
        return self._group(group_obj)

    def cidr(self, block, rating=None, confidence=None, xid=True):
        """Add CIDR data to Batch object.

        Args:
            block (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of CIDR.
        """
        indicator_obj = CIDR(block, rating, confidence, xid)
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
            # don't delete saved files
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
        data = {
            'group': [],
            'indicator': []
        }
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
                    'type': group_data.get('type')
                }
        else:
            # process file content
            if group_data.data.get('type') in ['Document', 'Report']:
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

    def document(self, name, file_name, file_content=None, malware=False, password=None, xid=True):
        """Add Document data to Batch object.

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached file for this Group.
            file_content (str;method, optional): The file contents or callback method to retrieve
                file content.
            malware (bool, default:False): If true the file is considered malware.
            password (bool, optional): If malware is true a password for the zip archive is
                required.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Document.
        """
        group_obj = Document(name, file_name, file_content, malware, password, xid)
        return self._group(group_obj)

    def email(self, name, subject, header, body, to_addr=None, from_addr=None, xid=True):
        """Add Email data to Batch object.

        Args:
            name (str): The name for this Group.
            subject (str): The subject for this Email.
            header (str): The header for this Email.
            body (str): The body for this Email.
            to_addr (str, optional): The **to** address for this Email.
            from_addr (str, optional): The **from** address for this Email.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Email.
        """
        group_obj = Email(name, subject, header, body, to_addr, from_addr, xid)
        return self._group(group_obj)

    def email_address(self, address, rating=None, confidence=None, xid=True):
        """Add Email Address data to Batch object.

        Args:
            address (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of EmailAddress.
        """
        indicator_obj = EmailAddress(address, rating, confidence, xid)
        return self._indicator(indicator_obj)

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
            r = self.tcex.session.get('/v2/batch/{}/errors'.format(batch_id))
            # if r.status_code == 404:
            #     time.sleep(5)  # allow time for errors to be processed
            #     r = self.tcex.session.get('/v2/batch/{}/errors'.format(batch_id))
            self.tcex.log.debug('Retrieve Errors for ID {}: status code {}, errors {}'.format(
                batch_id, r.status_code, r.text))
            # self.tcex.log.debug('Retrieve Errors URL {}'.format(r.url))
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

    def event(self, name, event_date=None, status=None, xid=True):
        """Add Event data to Batch object.

        Args:
            name (str): The name for this Group.
            event_date (str, optional): The event datetime expression for this Group.
            status (str, optional): The status for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Event.
        """
        group_obj = Event(name, event_date, status, xid)
        return self._group(group_obj)

    def file(self, md5=None, sha1=None, sha256=None, size=None, rating=None, confidence=None,
             xid=True):
        """Add File data to Batch object.

        .. note:: A least one file hash value must be specified.

        Args:
            md5 (str, optional): The md5 value for this Indicator.
            sha1 (str, optional): The sha1 value for this Indicator.
            sha256 (str, optional): The sha256 value for this Indicator.
            size (str, optional): The file size for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of File.
        """
        indicator_obj = File(md5, sha1, sha256, size, rating, confidence, xid)
        return self._indicator(indicator_obj)

    @property
    def files(self):
        """Return dictionary containing all of the file content or callbacks."""
        return self._files

    def generate_xid(self, identifier=None):
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

    def group(self, group_type, name, xid=True):
        """Add Group data to Batch object.

        Args:
            group_type (str): The ThreatConnect define Group type.
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Group.
        """
        group_obj = Group(group_type, name, xid)
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
                self.tcex.args.tc_temp_path, 'groups-{}'.format(str(uuid.uuid4())))

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
            # TODO: let gc close or implicit close? there could be significant overhead/delay in
            #       manually closing.
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

    def host(self, hostname, dns_active=False, whois_active=False, rating=None, confidence=None,
             xid=True):
        """Add Email Address data to Batch object.

        Args:
            hostname (str): The value for this Indicator.
            dns_active (bool, default:False): If True DNS active is enabled for this indicator.
            whois_active (bool, default:False): If True WhoIs active is enabled for this
                indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of Host.
        """
        indicator_obj = Host(hostname, dns_active, whois_active, rating, confidence, xid)
        return self._indicator(indicator_obj)

    def incident(self, name, event_date=None, status=None, xid=True):
        """Add Incident data to Batch object.

        Args:
            name (str): The name for this Group.
            event_date (str, optional): The event datetime expression for this Group.
            status (str, optional): The status for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Incident.
        """
        group_obj = Incident(name, event_date, status, xid)
        return self._group(group_obj)

    def indicator(self, indicator_type, summary, rating=None, confidence=None, xid=True):
        """Add Indicator data to Batch object.

        Args:
            indicator_type (str): The ThreatConnect define Indicator type.
            summary (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of Indicator.
        """
        indicator_obj = Indicator(indicator_type, summary, rating, confidence, xid)
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
                self.tcex.args.tc_temp_path, 'indicators-{}'.format(str(uuid.uuid4())))

            # saved shelf file
            if self.saved_indicators:
                self._indicator_shelf_fqfn = os.path.join(
                    self.tcex.args.tc_temp_path, 'indicators-saved')
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
            # TODO: let gc close or implicit close? there could be significant overhead/delay in
            #       manually closing.
            self._indicators_shelf = shelve.open(self.indicator_shelf_fqfn, writeback=False)
        return self._indicators_shelf

    def intrusion_set(self, name, xid=True):
        """Add Intrusion Set data to Batch object.

        Args:
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of IntrusionSet.
        """
        group_obj = IntrusionSet(name, xid)
        return self._group(group_obj)

    def mutex(self, mutex, rating=None, confidence=None, xid=True):
        """Add Mutex data to Batch object.

        Args:
            mutex (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of Mutex.
        """
        indicator_obj = Mutex(mutex, rating, confidence, xid)
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
            self._poll_interval = max(math.ceil(self._batch_data_count / 250), 5)
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
        params = {
            'includeAdditional': 'true'
        }

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
                self._poll_interval_times = self._poll_interval_times[-4:] + [(poll_time_total * .6)]

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
                self._poll_interval = math.floor(poll_interval_time_weighted_sum/sum(weights))

                if poll_count == 1:
                    # if completed on first poll, reduce poll interval.
                    self._poll_interval = self._poll_interval * .85

                self.tcex.log.debug('Batch Status: {}'.format(data))
                return data

            # update poll_interval for retry with max poll time of 20 seconds
            self._poll_interval = min(
                poll_retry_seconds + int(poll_count * poll_interval_back_off), 20)

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

    def registry_key(self, key_name, value_name, value_type, rating=None, confidence=None,
                     xid=True):
        """Add Registry Key data to Batch object.

        Args:
            key_name (str): The key_name value for this Indicator.
            value_name (str): The value_name value for this Indicator.
            value_type (str): The value_type value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of Registry Key.
        """
        indicator_obj = RegistryKey(key_name, value_name, value_type, rating, confidence, xid)
        return self._indicator(indicator_obj)

    def report(self, name, file_name, file_content=None, publish_date=None, xid=True):
        """Add Report data to Batch object.

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached file for this Group.
            file_content (str;method, optional): The file contents or callback method to retrieve
                file content.
            publish_date (str, optional): The publish datetime expression for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Report.
        """
        group_obj = Report(name, file_name, file_content, publish_date, xid)
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
            if (self.enable_saved_file and os.path.isfile(fqfn_saved) and
                    os.access(fqfn_saved, os.R_OK)):
                self._saved_groups = True
                self.tcex.log.debug('groups-saved file found')
        return self._saved_groups

    @property
    def saved_indicators(self):
        """Return True if saved indicators files exits, else False."""
        if self._saved_indicators is None:
            self._saved_indicators = False
            fqfn_saved = os.path.join(self.tcex.args.tc_temp_path, 'indicators-saved')
            if (self.enable_saved_file and os.path.isfile(fqfn_saved) and
                    os.access(fqfn_saved, os.R_OK)):
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
        return {
            'action': self._action,
            # not supported in v2 batch
            # 'attributeWriteType': self._attribute_write_type,
            'attributeWriteType': 'Replace',
            'haltOnError': str(self._halt_on_error).lower(),
            'owner': self._owner,
            'version': 'V2'
        }

    def signature(self, name, file_name, file_type, file_text, xid=True):
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
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Signature.
        """
        group_obj = Signature(name, file_name, file_type, file_text, xid)
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
        batch_data = self.submit_create_and_upload(
            halt_on_error).get('data', {}).get('batchStatus', {})
        batch_id = batch_data.get('id')
        if batch_id is not None:
            # job hit queue
            if poll:
                # poll for status
                batch_data = self.poll(
                    batch_id, halt_on_error=halt_on_error).get('data', {}).get('batchStatus')
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
                if len(self) > 0:
                    batch_id = self.submit_job(halt_on_error)
                    if batch_id is not None:
                        batch_data = self.submit_data(batch_id, halt_on_error)
                else:
                    batch_data = {}
            else:
                batch_data = self.submit_create_and_upload(
                    halt_on_error).get('data', {}).get('batchStatus', {})
                batch_id = batch_data.get('id')

            if not batch_data:
                break
            elif batch_id is not None:
                self.tcex.log.info('Batch ID: {}'.format(batch_id))
                # job hit queue
                if poll:
                    # poll for status
                    batch_data = self.poll(
                        batch_id, halt_on_error=halt_on_error).get('data', {}).get('batchStatus')
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
        return batch_data_array

    def submit_create_and_upload(self, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.

        Returns.
            dict: The Batch Status from the ThreatConnect API.
        """
        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        content = self.data
        # store the length of the batch data to use for poll interval calculations
        self._batch_data_count = len(content.get('group')) + len(content.get('indicator'))
        self.tcex.log.info('Batch Size: {:,}'.format(self._batch_data_count))
        if self.debug:
            # special code for debugging App using batchV2.
            self.write_batch_json(content)
        if content.get('group') or content.get('indicator'):
            try:
                files = (
                    ('config', json.dumps(self.settings)),
                    ('content', json.dumps(content))
                )
                params = {
                    'includeAdditional': 'true'
                }
                r = self.tcex.session.post('/v2/batch/createAndUpload', files=files, params=params)
                self.tcex.log.debug('Batch Status Code: {}'.format(r.status_code))
            except Exception as e:
                self.tcex.handle_error(1505, [e], halt_on_error)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.tcex.handle_error(1510, [r.status_code, r.text], halt_on_error)
            return r.json()
        return {}

    def submit_data(self, batch_id, halt_on_error=True):
        """Submit Batch request to ThreatConnect API.
        Args:
            batch_id (string): The batch id of the current job.
        """
        # check global setting for override
        if self.halt_on_batch_error is not None:
            halt_on_error = self.halt_on_batch_error

        content = self.data
        # store the length of the batch data to use for poll interval calculations
        self._batch_data_count = len(content.get('group')) + len(content.get('indicator'))
        self.tcex.log.info('Batch Size: {:,}'.format(self._batch_data_count))
        if content.get('group') or content.get('indicator'):
            headers = {'Content-Type': 'application/octet-stream'}
            try:
                r = self.tcex.session.post(
                    '/v2/batch/{}'.format(batch_id), headers=headers, json=content)
            except Exception as e:
                self.tcex.handle_error(1520, [e], halt_on_error)
            if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                self.tcex.handle_error(1525, [r.status_code, r.text], halt_on_error)
            return r.json()
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
        for xid, content_data in self._files.items():
            del self._files[xid]  # win or loose remove the entry
            status = True

            # used for debug/testing to prevent upload of previously uploaded file
            if self.debug and xid in self.saved_xids:
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
            params = {'owner': self._owner}
            r = self.submit_file_content('POST', url, content, headers, params, halt_on_error)
            if r.status_code == 401:
                # use PUT method if file already exists
                self.tcex.log.info('Received 401 status code using POST. Trying PUT to update.')
                r = self.submit_file_content('PUT', url, content, headers, params, halt_on_error)
            self.tcex.log.debug('{} Upload URL: {}.'.format(content_data.get('type'), r.url))
            if not r.ok:
                status = False
                self.tcex.handle_error(585, [r.status_code, r.text], halt_on_error)
            elif self.debug:
                self.saved_xids.append(xid)
            self.tcex.log.info('Status {} for file upload with xid {}.'.format(
                r.status_code, xid))
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
            self.tcex.handle_error(1505, [e], halt_on_error)
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.tcex.handle_error(1510, [r.status_code, r.text], halt_on_error)
        data = r.json()
        if data.get('status') != 'Success':
            self.tcex.handle_error(1510, [r.status_code, r.text], halt_on_error)
        self.tcex.log.debug('Batch Submit Data: {}'.format(data))
        return data.get('data', {}).get('batchId')

    def threat(self, name, xid=True):
        """Add Threat data to Batch object

        Args:
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.

        Returns:
            obj: An instance of Threat.
        """
        group_obj = Threat(name, xid)
        return self._group(group_obj)

    def user_agent(self, text, rating=None, confidence=None, xid=True):
        """Add User Agent data to Batch object

        Args:
            text (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of UserAgent.
        """
        indicator_obj = UserAgent(text, rating, confidence, xid)
        return self._indicator(indicator_obj)

    def url(self, text, rating=None, confidence=None, xid=True):
        """Add URL Address data to Batch object.

        Args:
            text (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.

        Returns:
            obj: An instance of URL.
        """
        indicator_obj = URL(text, rating, confidence, xid)
        return self._indicator(indicator_obj)

    def write_batch_json(self, content):
        """Write batch json data to a file."""
        timestamp = str(time.time()).replace('.', '')
        batch_json_file = os.path.join(
            self.tcex.args.tc_temp_path, 'batch-{}.json'.format(timestamp))
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

        data = {
            'group': groups,
            'indicators': indicators
        }
        return json.dumps(data, indent=4, sort_keys=True)


#
# Groups
#


class Group(object):
    """ThreatConnect Batch Group Object"""

    def __init__(self, group_type, name, xid=True):
        """Initialize Class Properties.

        Args:
            group_type (str): The ThreatConnect define Group type.
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.
        """
        self._name = name
        self._type = group_type
        self._group_data = {
            'name': name,
            'type': group_type,
            'xid': self._xid(xid)
        }
        self._attributes = []
        self._labels = []
        self._tags = []
        # processed
        self._processed = False
        self._utils = TcExUtils()

    def _xid(self, xid):
        """Return a valid xid."""
        if xid is True or xid is None:
            # generate a reproducible value for xid
            xid_string = '{}-{}'.format(self._type, self._name)
            hash_object = hashlib.sha256(xid_string.encode('utf-8'))
            xid = hash_object.hexdigest()
        elif xid is False:
            # generate a random value for xid
            xid = str(uuid.uuid4())

        return xid

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
        self._group_data[key] = value

    def association(self, group_xid):
        """Add association using xid value.

        Args:
            group_xid (str): The external id of the Group to associate.
        """
        self._group_data.setdefault('associatedGroupXid', []).append(group_xid)

    def attribute(self, attr_type, attr_value, displayed=False, source=None, unique=True,
                  formatter=None):
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
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)


class Adversary(Group):
    """ThreatConnect Batch Adversary Object"""

    def __init__(self, name, xid=True):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.
        """
        super(Adversary, self).__init__('Adversary', name, xid)


class Campaign(Group):
    """ThreatConnect Batch Campaign Object"""

    def __init__(self, name, first_seen=None, xid=True):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            first_seen (str, optional): The first see datetime expression for this Group.
            xid (str, optional): The external id for this Group.
        """
        super(Campaign, self).__init__('Campaign', name, xid)
        if first_seen is not None:
            self._group_data['firstSeen'] = self._utils.format_datetime(
                first_seen, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def first_seen(self):
        """Return Document first seen."""
        return self._group_data.get('firstSeen')

    @first_seen.setter
    def first_seen(self, first_seen):
        """Set Document first seen."""
        self._group_data['firstSeen'] = self._utils.format_datetime(
            first_seen, date_format='%Y-%m-%dT%H:%M:%SZ')


class Document(Group):
    """ThreatConnect Batch Document Object"""

    def __init__(self, name, file_name, file_content=None, malware=False, password=None,
                 xid=True):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached file for this Group.
            file_content (str;method, optional): The file contents or callback method to retrieve
                file content.
            malware (bool, default:False): If true the file is considered malware.
            password (bool, optional): If malware is true a password for the zip archive is
                required.
            xid (str, optional): The external id for this Group.
        """
        super(Document, self).__init__('Document', name, xid)
        self._group_data['fileName'] = file_name
        # file data/content to upload
        self._file_data = {
            'fileContent': file_content,
            'fileName': file_name,
            'type': self._group_data.get('type')
        }
        if malware:
            self._group_data['malware'] = malware
        if password is not None:
            self._group_data['password'] = password

    @property
    def file_content(self):
        """Return Group files."""
        return self._file_data.get('fileContent')

    @file_content.setter
    def file_content(self, file_content):
        """Set Document or Report file data."""
        self._file_data['fileContent'] = file_content

    @property
    def file_data(self):
        """Return Group files."""
        return self._file_data

    @property
    def malware(self):
        """Return Document malware."""
        return self._group_data.get('malware', False)

    @malware.setter
    def malware(self, malware):
        """Set Document malware."""
        self._group_data['malware'] = malware

    @property
    def password(self):
        """Return Document password."""
        return self._group_data.get('password', False)

    @password.setter
    def password(self, password):
        """Set Document password."""
        self._group_data['password'] = password


class Email(Group):
    """ThreatConnect Batch Email Object"""

    def __init__(self, name, subject, header, body, to_addr=None, from_addr=None, xid=True):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            subject (str): The subject for this Email.
            header (str): The header for this Email.
            body (str): The body for this Email.
            to_addr (str, optional): The **to** address for this Email.
            from_addr (str, optional): The **from** address for this Email.
            xid (str, optional): The external id for this Group.
        """
        super(Email, self).__init__('Email', name, xid)
        self._group_data['subject'] = subject
        self._group_data['header'] = header
        self._group_data['body'] = body
        self._group_data['score'] = 0
        if to_addr is not None:
            self._group_data['to'] = to_addr
        if from_addr is not None:
            self._group_data['from'] = from_addr

    @property
    def from_addr(self):
        """Return Email to."""
        return self._group_data.get('to')

    @from_addr.setter
    def from_addr(self, from_addr):
        """Set Email from."""
        self._group_data['from'] = from_addr

    @property
    def score(self):
        """Return Email to."""
        return self._group_data.get('score')

    @score.setter
    def score(self, score):
        """Set Email from."""
        self._group_data['score'] = score

    @property
    def to_addr(self):
        """Return Email to."""
        return self._group_data.get('to')

    @to_addr.setter
    def to_addr(self, to_addr):
        """Set Email to."""
        self._group_data['to'] = to_addr


class Event(Group):
    """ThreatConnect Batch Event Object"""

    def __init__(self, name, event_date=None, status=None, xid=True):
        """Initialize Class Properties.

        Valid Values:
        + Escalated
        + False Positive
        + Needs Review
        + No Further Action

        Args:
            name (str): The name for this Group.
            event_date (str, optional): The event datetime expression for this Group.
            status (str, optional): The status for this Group.
            xid (str, optional): The external id for this Group.
        """
        super(Event, self).__init__('Event', name, xid)
        if event_date is not None:
            self._group_data['eventDate'] = self._utils.format_datetime(
                event_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        if status is not None:
            self._group_data['status'] = status

    @property
    def event_date(self):
        """Return the Events "event date" value."""
        return self._group_data.get('firstSeen')

    @event_date.setter
    def event_date(self, event_date):
        """Set the Events "event date" value."""
        self._group_data['eventDate'] = self._utils.format_datetime(
            event_date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def status(self):
        """Return the Events status value."""
        return self._group_data.get('status')

    @status.setter
    def status(self, status):
        """Set the Events status value."""
        self._group_data['status'] = status


class Incident(Group):
    """ThreatConnect Batch Incident Object"""

    def __init__(self, name, event_date=None, status=None, xid=True):
        """Initialize Class Properties.

        Valid Values:
        + Closed
        + Containment Achieved
        + Deleted
        + Incident Reported
        + Open
        + New
        + Rejected
        + Restoration Achieved
        + Stalled

        Args:
            name (str): The name for this Group.
            event_date (str, optional): The event datetime expression for this Group.
            status (str, optional): The status for this Group.
            xid (str, optional): The external id for this Group.
        """
        super(Incident, self).__init__('Incident', name, xid)
        if event_date is not None:
            self._group_data['eventDate'] = self._utils.format_datetime(
                event_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        if status is not None:
            self._group_data['status'] = status

    @property
    def event_date(self):
        """Return Incident event date."""
        return self._group_data.get('eventDate')

    @event_date.setter
    def event_date(self, event_date):
        """Set Incident event_date."""
        self._group_data['eventDate'] = self._utils.format_datetime(
            event_date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def status(self):
        """Return Incident status."""
        return self._group_data.get('status')

    @status.setter
    def status(self, status):
        """Set Incident status.

        Valid Values:
        + New
        + Open
        + Stalled
        + Containment Achieved
        + Restoration Achieved
        + Incident Reported
        + Closed
        + Rejected
        + Deleted
        """
        self._group_data['status'] = status


class IntrusionSet(Group):
    """ThreatConnect Batch Adversary Object"""

    def __init__(self, name, xid=True):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.
        """
        super(IntrusionSet, self).__init__('Intrusion Set', name, xid)


class Report(Group):
    """ThreatConnect Batch Report Object"""

    def __init__(self, name, file_name=None, file_content=None, publish_date=None, xid=True):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            file_name (str): The name for the attached file for this Group.
            file_content (str;method, optional): The file contents or callback method to retrieve
                file content.
            publish_date (str, optional): The publish datetime expression for this Group.
            xid (str, optional): The external id for this Group.
        """
        super(Report, self).__init__('Report', name, xid)
        self._group_data['fileName'] = file_name
        # file data/content to upload
        self._file_data = {
            'fileContent': file_content,
            'fileName': file_name,
            'type': self._group_data.get('type')
        }
        if publish_date is not None:
            self._group_data['publishDate'] = self._utils.format_datetime(
                publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def file_content(self):
        """Return Group files."""
        return self._file_data.get('fileContent')

    @file_content.setter
    def file_content(self, file_content):
        """Set Document or Report file data."""
        self._file_data['fileContent'] = file_content

    @property
    def file_data(self):
        """Return Group files."""
        return self._file_data

    @property
    def publish_date(self):
        """Return Report publish date."""
        return self._group_data.get('publishDate')

    @publish_date.setter
    def publish_date(self, publish_date):
        """Set Report publish date"""
        self._group_data['publishDate'] = self._utils.format_datetime(
            publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')


class Signature(Group):
    """ThreatConnect Batch Signature Object"""

    def __init__(self, name, file_name, file_type, file_text, xid=True):
        """Initialize Class Properties.

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
            xid (str, optional): The external id for this Group.
        """
        super(Signature, self).__init__('Signature', name, xid)
        self._group_data['fileName'] = file_name
        self._group_data['fileType'] = file_type
        self._group_data['fileText'] = file_text


class Threat(Group):
    """ThreatConnect Batch Threat Object"""

    def __init__(self, name, xid=True):
        """Initialize Class Properties.

        Args:
            name (str): The name for this Group.
            xid (str, optional): The external id for this Group.
        """
        super(Threat, self).__init__('Threat', name, xid)


#
# Indicators
#


class Indicator(object):
    """ThreatConnect Batch Indicator Object"""

    def __init__(self, indicator_type, summary, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            indicator_type (str): The ThreatConnect define Indicator type.
            summary (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        self._summary = summary
        self._type = indicator_type
        self._indicator_data = {
            'summary': summary,
            'type': indicator_type,
            'xid': self._xid(xid)
        }
        if confidence is not None:
            self._indicator_data['confidence'] = int(confidence)
        if rating is not None:
            self._indicator_data['rating'] = float(rating)
        self._attributes = []
        self._file_actions = []
        self._labels = []
        self._occurrences = []
        self._tags = []
        self._utils = TcExUtils()

    def _xid(self, xid):
        """Return a valid xid."""
        if xid is True or xid is None:
            # generate a reproducible value for xid
            xid_string = '{}-{}'.format(self._type, self._summary)
            hash_object = hashlib.sha256(xid_string.encode('utf-8'))
            xid = hash_object.hexdigest()
        elif xid is False:
            # generate a random value for xid
            xid = str(uuid.uuid4())

        return xid

    def add_key_value(self, key, value):
        """Add custom field to Indicator object.

        .. note:: The key must be the exact name required by the batch schema.

        Example::

            file_hash = tcex.batch.file('File', '1d878cdc391461e392678ba3fc9f6f32')
            file_hash.add_key_value('size', '1024')

        Args:
            key (str): The field key to add to the JSON batch data.
            value (str): The field value to add to the JSON batch data.
        """
        if self._indicator_data.get('type') == 'File':
            if key == 'size':
                key = 'intValue1'
        if self._indicator_data.get('type') == 'Host':
            if key == 'dnsActive':
                key = 'flag1'
            elif key == 'whoisActive':
                key = 'flag2'
        self._indicator_data[key] = value

    @property
    def active(self):
        """Return Indicator active."""
        return self._indicator_data.get('active')

    @active.setter
    def active(self, active):
        """Set Indicator active."""
        self._indicator_data['active'] = self._utils.to_bool(active)

    def association(self, group_xid):
        """Add association using xid value.

        Args:
            group_xid (str): The external id of the Group to associate.
        """
        association = {'groupXid': group_xid}
        self._indicator_data.setdefault('associatedGroups', []).append(association)

    def attribute(self, attr_type, attr_value, displayed=False, source=None, unique=True,
                  formatter=None):
        """Return instance of Attribute

        unique:
            * False - Attribute type:value can be duplicated.
            * Type - Attribute type has to be unique (e.g., only 1 Description Attribute).
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
                    attr = attribute_data
                    break
            else:
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

    def build_summary(self, val1=None, val2=None, val3=None):
        """Build the Indicator summary using available values."""
        summary = []
        if val1 is not None:
            summary.append(val1)
        if val2 is not None:
            summary.append(val2)
        if val3 is not None:
            summary.append(val3)
        if not summary:
            ## BCS
            # self.tcex.handle_error(590)
            pass
        return ' : '.join(summary)

    @property
    def confidence(self):
        """Return Indicator confidence."""
        return self._indicator_data.get('confidence')

    @confidence.setter
    def confidence(self, confidence):
        """Set Indicator confidence."""
        self._indicator_data['confidence'] = int(confidence)

    @property
    def data(self):
        """Return Indicator data."""
        # add attributes
        if self._attributes:
            self._indicator_data['attribute'] = []
            for attr in self._attributes:
                if attr.valid:
                    self._indicator_data['attribute'].append(attr.data)
        # add file actions
        if self._file_actions:
            self._indicator_data.setdefault('fileAction', {})
            self._indicator_data['fileAction'].setdefault('children', [])
            for action in self._file_actions:
                self._indicator_data['fileAction']['children'].append(action.data)
        # add file occurrences
        if self._occurrences:
            self._indicator_data.setdefault('fileOccurrence', [])
            for occurrence in self._occurrences:
                self._indicator_data['fileOccurrence'].append(occurrence.data)
        # add security labels
        if self._labels:
            self._indicator_data['securityLabel'] = []
            for label in self._labels:
                self._indicator_data['securityLabel'].append(label.data)
        # add tags
        if self._tags:
            self._indicator_data['tag'] = []
            for tag in self._tags:
                if tag.valid:
                    self._indicator_data['tag'].append(tag.data)
        return self._indicator_data

    def occurrence(self, file_name=None, path=None, date=None):
        """Add a file Occurrence.

        Args:
            file_name (str, optional): The file name for this occurrence.
            path (str, optional): The file path for this occurrence.
            date (str, optional): The datetime expression for this occurrence.

        Returns:
            obj: An instance of Occurrence.
        """
        if self._indicator_data.get('type') != 'File':
            ## BCS
            # self.tcex.handle_error(520, [self._indicator_data.get('type')], True)
            pass

        occurrence_obj = FileOccurrence(file_name, path, date)
        self._occurrences.append(occurrence_obj)
        return occurrence_obj

    @property
    def private_flag(self):
        """Return Indicator private flag."""
        return self._indicator_data.get('privateFlag')

    @private_flag.setter
    def private_flag(self, private_flag):
        """Set Indicator private flag."""
        self._indicator_data['privateFlag'] = self._utils.to_bool(private_flag)

    @property
    def rating(self):
        """Return Indicator rating."""
        return self._indicator_data.get('rating')

    @rating.setter
    def rating(self, rating):
        """Set Indicator rating."""
        self._indicator_data['rating'] = float(rating)

    @property
    def summary(self):
        """Return Indicator summary."""
        return self._indicator_data.get('summary')

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
        return self._indicator_data.get('type')

    @property
    def xid(self):
        """Return Group xid."""
        return self._indicator_data.get('xid')

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class Address(Indicator):
    """ThreatConnect Batch Address Object"""

    def __init__(self, ip, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            ip (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(Address, self).__init__('Address', ip, rating, confidence, xid)


class ASN(Indicator):
    """ThreatConnect Batch ASN Object."""

    def __init__(self, as_number, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            as_number (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(ASN, self).__init__('ASN', as_number, rating, confidence, xid)


class CIDR(Indicator):
    """ThreatConnect Batch CIDR Object"""

    def __init__(self, block, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            block (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(CIDR, self).__init__('CIDR', block, rating, confidence, xid)


class EmailAddress(Indicator):
    """ThreatConnect Batch EmailAddress Object"""

    def __init__(self, address, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            address (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(EmailAddress, self).__init__('EmailAddress', address, rating, confidence, xid)


class File(Indicator):
    """ThreatConnect Batch File Object"""

    def __init__(self, md5=None, sha1=None, sha256=None, size=None, rating=None,
                 confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            md5 (str, optional): The md5 value for this Indicator.
            sha1 (str, optional): The sha1 value for this Indicator.
            sha256 (str, optional): The sha256 value for this Indicator.
            size (str, optional): The file size for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        summary = self.build_summary(md5, sha1, sha256)  # build the indicator summary
        super(File, self).__init__('File', summary, rating, confidence, xid)
        self._indicator_data['type'] = 'File'
        if size is not None:
            self._indicator_data['intValue1'] = size
        # self._file_action = []

    def action(self, relationship):
        """Add a File Action."""
        action_obj = FileAction(self._indicator_data.get('xid'), relationship)
        self._file_actions.append(action_obj)
        return action_obj

    @property
    def md5(self):
        """Return Indicator md5."""
        return self._indicator_data.get('md5')

    @md5.setter
    def md5(self, md5):
        """Set Indicator md5."""
        self._indicator_data['md5'] = md5

    @property
    def sha1(self):
        """Return Indicator sha1."""
        return self._indicator_data.get('sha1')

    @sha1.setter
    def sha1(self, sha1):
        """Set Indicator sha1."""
        self._indicator_data['sha1'] = sha1

    @property
    def sha256(self):
        """Return Indicator sha256."""
        return self._indicator_data.get('sha256')

    @sha256.setter
    def sha256(self, sha256):
        """Set Indicator sha256."""
        self._indicator_data['sha256'] = sha256

    @property
    def size(self):
        """Return Indicator size."""
        return self._indicator_data.get('intValue1')

    @size.setter
    def size(self, size):
        """Set Indicator size."""
        self._indicator_data['intValue1'] = size


class Host(Indicator):
    """ThreatConnect Batch Host Object"""

    def __init__(self, hostname, dns_active=False, whois_active=False, rating=None,
                 confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            hostname (str): The value for this Indicator.
            dns_active (bool, default:False): If True DNS active is enabled for this indicator.
            whois_active (bool, default:False): If True WhoIs active is enabled for this
                indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(Host, self).__init__('Host', hostname, rating, confidence, xid)
        if dns_active:
            self._indicator_data['flag1'] = dns_active
        if whois_active:
            self._indicator_data['flag2'] = dns_active

    @property
    def dns_active(self):
        """Return Indicator dns active."""
        return self._indicator_data.get('flag1')

    @dns_active.setter
    def dns_active(self, dns_active):
        """Set Indicator dns active."""
        self._indicator_data['flag1'] = dns_active

    @property
    def whois_active(self):
        """Return Indicator whois active."""
        return self._indicator_data.get('flag2')

    @whois_active.setter
    def whois_active(self, whois_active):
        """Set Indicator whois active."""
        self._indicator_data['flag2'] = whois_active


class Mutex(Indicator):
    """ThreatConnect Batch Mutex Object"""

    def __init__(self, mutex, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            mutex (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(Mutex, self).__init__('Mutex', mutex, rating, confidence, xid)


class RegistryKey(Indicator):
    """ThreatConnect Batch Registry Key Object"""

    def __init__(self, key_name, value_name, value_type, rating=None, confidence=None,
                 xid=True):
        """Initialize Class Properties.

        Args:
            key_name (str): The key_name value for this Indicator.
            value_name (str): The value_name value for this Indicator.
            value_type (str): The value_type value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        summary = self.build_summary(key_name, value_name, value_type)
        super(RegistryKey, self).__init__('Registry Key', summary, rating, confidence, xid)


class URL(Indicator):
    """ThreatConnect Batch URL Object"""

    def __init__(self, text, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            text (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(URL, self).__init__('URL', text, rating, confidence, xid)


class UserAgent(Indicator):
    """ThreatConnect Batch User Agent Object"""

    def __init__(self, text, rating=None, confidence=None, xid=True):
        """Initialize Class Properties.

        Args:
            text (str): The value for this Indicator.
            rating (str, optional): The threat rating for this Indicator.
            confidence (str, optional): The threat confidence for this Indicator.
            xid (str, optional): The external id for this Indicator.
        """
        super(UserAgent, self).__init__('User Agent', text, rating, confidence, xid)


#
# Metadata Classes
#


class Attribute(object):
    """ThreatConnect Batch Attribute Object"""

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
        self._attribute_data = {
            'type': attr_type
        }
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
        if not attr_value:
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


class FileAction(object):
    """ThreatConnect Batch FileAction Object"""

    def __init__(self, parent_xid, relationship):
        """Initialize Class Properties.

        .. warning:: This code is not complete and may require some update to the API.

        Args:
            parent_xid (str): The external id of the parent Indicator.
            relationship: ???
        """
        self.xid = str(uuid.uuid4())
        self._action_data = {
            'indicatorXid': self.xid,
            'relationship': relationship,
            'parentIndicatorXid': parent_xid
        }
        self._children = []

    @property
    def data(self):
        """Return File Occurrence data."""
        if self._children:
            for child in self._children:
                self._action_data.setdefault('children', []).append(child.data)
        return self._action_data

    def action(self, relationship):
        """Add a nested File Action."""
        action_obj = FileAction(self.xid, relationship)
        self._children.append(action_obj)

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)


class FileOccurrence(object):
    """ThreatConnect Batch FileAction Object."""

    def __init__(self, file_name=None, path=None, date=None):
        """Initialize Class Properties

        Args:
            file_name (str, optional): The file name for this occurrence.
            path (str, optional): The file path for this occurrence.
            date (str, optional): The datetime expression for this occurrence.
        """
        self._utils = TcExUtils()
        self._occurrence_data = {}
        if file_name is not None:
            self._occurrence_data['fileName'] = file_name
        if path is not None:
            self._occurrence_data['path'] = path
        if date is not None:
            self._occurrence_data['date'] = self._utils.format_datetime(
                date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def data(self):
        """Return File Occurrence data."""
        return self._occurrence_data

    @property
    def date(self):
        """Return File Occurrence date."""
        return self._occurrence_data.get('date')

    @date.setter
    def date(self, date):
        """Set File Occurrence date."""
        self._occurrence_data['date'] = self._utils.format_datetime(
            date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def file_name(self):
        """Return File Occurrence file name."""
        return self._occurrence_data.get('fileName')

    @file_name.setter
    def file_name(self, file_name):
        """Set File Occurrence file name."""
        self._occurrence_data['fileName'] = file_name

    @property
    def path(self):
        """Return File Occurrence path."""
        return self._occurrence_data.get('path')

    @path.setter
    def path(self, path):
        """Set File Occurrence path."""
        self._occurrence_data['path'] = path

    def __str__(self):
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)


class SecurityLabel(object):
    """ThreatConnect Batch SecurityLabel Object."""

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

    def __init__(self, name, formatter=None):
        """Initialize Class Properties.

        Args:
            name (str): The value for this tag.
            formatter (method, optional): A method that take a tag value and returns a
                formatted tag.
        """
        if formatter is not None:
            name = formatter(name)
        self._tag_data = {
            'name': name
        }
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
