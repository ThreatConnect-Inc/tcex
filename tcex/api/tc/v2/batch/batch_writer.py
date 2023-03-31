"""TcEx Framework Module"""
# standard library
import gzip
import hashlib
import json
import logging
import os
import re
import shelve  # nosec
import sys
import time
import uuid
from collections import deque
from typing import Any

# third-party
from requests import Session  # TYPE-CHECKING

# first-party
from tcex.api.tc.util.threat_intel_util import ThreatIntelUtil
from tcex.api.tc.v2.batch.group import (
    Adversary,
    AttackPattern,
    Campaign,
    CourseOfAction,
    Document,
    Email,
    Event,
    Group,
    Incident,
    IntrusionSet,
    Malware,
    Report,
    Signature,
    Tactic,
    Threat,
    Tool,
    Vulnerability,
)
from tcex.api.tc.v2.batch.indicator import (
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
from tcex.input.input import Input  # TYPE-CHECKING
from tcex.logger.trace_logger import TraceLogger
from tcex.util import Util

# import local modules for dynamic reference
module = __import__(__name__)

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore

# define GroupType
GroupType = (
    Adversary
    | AttackPattern
    | Campaign
    | CourseOfAction
    | Document
    | Email
    | Event
    | Group
    | Incident
    | IntrusionSet
    | Malware
    | Report
    | Signature
    | Tactic
    | Threat
    | Tool
    | Vulnerability
)

# define IndicatorType
IndicatorType = (
    ASN
    | CIDR
    | URL
    | Address
    | EmailAddress
    | File
    | Host
    | Indicator
    | Mutex
    | RegistryKey
    | UserAgent
)


class BatchWriter:
    """ThreatConnect Batch Import Module

    Args:
        inputs: The App inputs.
        session_tc: The ThreatConnect API session.
        output_dir: The directory to write the batch JSON data.
    """

    def __init__(self, inputs: Input, session_tc: Session, output_dir: str, **kwargs):
        """Initialize instance properties."""
        self.inputs = inputs
        self.output_dir = output_dir
        self.output_extension = kwargs.get('output_extension')
        self.session_tc = session_tc
        self.write_callback = kwargs.get('write_callback')
        self.write_callback_kwargs = kwargs.get('write_callback_kwargs', {})

        # properties
        self._batch_files = []
        self._batch_max_chunk = 100_000
        self._batch_size = 0  # track current batch size
        self._batch_max_size = 75_000_000  # max size in bytes
        self.log = _logger
        self.tic = ThreatIntelUtil(self.session_tc)
        self.util = Util()

        # shelf settings
        self._group_shelf_fqfn = None
        self._indicator_shelf_fqfn = None

        # containers
        self._groups = None
        self._groups_shelf = None
        self._indicators = None
        self._indicators_shelf = None

        # build custom indicator classes
        self._gen_indicator_class()

    def _gen_indicator_class(self):  # pragma: no cover
        """Generate Custom Indicator Classes."""
        for entry in self.tic.indicator_types_data.values():
            name = entry['name']
            class_name = name.replace(' ', '')
            # temp fix for API issue where boolean are returned as strings
            entry['custom'] = self.util.to_bool(entry.get('custom') or False)

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

    def _gen_indicator_method(
        self, name: str, custom_class: Any, value_count: int
    ):  # pragma: no cover
        """Dynamically generate custom Indicator methods.

        Args:
            name: The name of the method.
            custom_class: The class to add.
            value_count: The number of value parameters to support.
        """
        method_name = name.replace(' ', '_').lower()

        # Add Method for each Custom Indicator class
        def method_1(value1: str, xid, **kwargs):  # pylint: disable=possibly-unused-variable
            """Add Custom Indicator data to Batch"""
            indicator_obj = custom_class(value1, xid, **kwargs)
            return self._indicator(indicator_obj, kwargs.get('store', True))

        def method_2(
            value1: str, value2: str, xid, **kwargs
        ):  # pylint: disable=possibly-unused-variable
            """Add Custom Indicator data to Batch"""
            indicator_obj = custom_class(value1, value2, xid, **kwargs)
            return self._indicator(indicator_obj, kwargs.get('store', True))

        def method_3(
            value1: str, value2: str, value3: str, xid, **kwargs
        ):  # pylint: disable=possibly-unused-variable
            """Add Custom Indicator data to Batch"""
            indicator_obj = custom_class(value1, value2, value3, xid, **kwargs)
            return self._indicator(indicator_obj, kwargs.get('store', True))

        method = locals()[f'method_{value_count}']
        setattr(self, method_name, method)

    def _group(self, group_data: dict | GroupType, store: bool = True) -> dict | GroupType:
        """Return previously stored group or new group.

        Args:
            group_data: An Group dict or instance of a GroupType.
            store: If True the group data will be stored in instance list.
        """
        if store is False:
            return group_data

        if isinstance(group_data, dict):
            # get xid from dict
            xid = group_data['xid']
        else:
            # get xid from GroupType
            xid = group_data.xid

        if self.groups.get(xid) is not None:
            # return existing group from memory
            group_data = self.groups[xid]
        elif self.groups_shelf.get(xid) is not None:
            # return existing group from shelf
            group_data = self.groups_shelf[xid]
        else:
            # store new group
            self.groups[xid] = group_data

            # track total batch job data size as TI gets added
            if isinstance(group_data, dict):
                self._batch_size += sys.getsizeof(json.dumps(group_data))
            else:
                self._batch_size += sys.getsizeof(json.dumps(group_data.data))

            # max size hit, dump TI to disk
            if self._batch_size > self._batch_max_size:
                self.dump()
        return group_data

    def _indicator(
        self, indicator_data: dict | IndicatorType, store: bool = True
    ) -> dict | IndicatorType:
        """Return previously stored indicator or new indicator.

        Args:
            indicator_data: An Indicator dict or instance of IndicatorType.
            store: If True the indicator data will be stored in instance list.
        """
        if store is False:
            return indicator_data

        if isinstance(indicator_data, dict):
            # get xid from dict
            xid = indicator_data['xid']
        else:
            # get xid from IndicatorType
            xid = indicator_data.xid

        if self.indicators.get(xid) is not None:
            # return existing indicator from memory
            indicator_data = self.indicators[xid]
        elif self.indicators_shelf.get(xid) is not None:
            # return existing indicator from shelf
            indicator_data = self.indicators_shelf[xid]
        else:
            # store new indicators
            self.indicators[xid] = indicator_data

            # track total batch job data size as TI gets added
            if isinstance(indicator_data, dict):
                self._batch_size += sys.getsizeof(json.dumps(indicator_data))
            else:
                self._batch_size += sys.getsizeof(json.dumps(indicator_data.data))

            # max size hit, dump TI to disk
            if self._batch_size > self._batch_max_size:
                self.dump()
        return indicator_data

    @staticmethod
    def _indicator_values(indicator: str) -> list:
        """Process indicators expanding file hashes/custom indicators into multiple entries.

        Args:
            indicator: Indicator value represented as " : " delimited string.

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

    def add_group(self, group_data: dict, **kwargs) -> dict | GroupType:
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
            group_data: The full Group data including attributes, labels, tags, and
                associations.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            (dict|GroupType): The new group dict/GroupType or the previously stored dict/GroupType.
        """
        return self._group(group_data, kwargs.get('store', True))

    def add_indicator(self, indicator_data: dict, **kwargs) -> dict | IndicatorType:
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
            indicator_data: The Full Indicator data including attributes, labels, tags,
                and associations.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            (dict|IndicatorType): The new group dict/IndicatorType
            or the previously stored dict/IndicatorType.
        """
        if indicator_data.get('type') not in ['Address', 'EmailAddress', 'File', 'Host', 'URL']:
            # for custom indicator types the valueX fields are required.
            # using the summary we can build the values
            index = 1
            for value in self._indicator_values(indicator_data['summary']):
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

        return self._indicator(indicator_data, kwargs.get('store', True))

    def address(self, ip: str, **kwargs) -> Address | dict:
        """Add Address data to Batch.

        Args:
            ip: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Address: An instance of the Address class.
        """
        indicator_obj = Address(ip, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def adversary(self, name: str, **kwargs) -> Adversary:
        """Add Adversary data to Batch.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Adversary: An instance of the Adversary class.
        """
        group_obj = Adversary(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def attack_pattern(self, name: str, **kwargs) -> AttackPattern:
        """Add Attack Pattern data to Batch object.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            AttackPattern: An instance of the AttackPattern class.
        """
        group_obj = AttackPattern(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def asn(self, as_number: str, **kwargs) -> ASN:
        """Add ASN data to Batch.

        Args:
            as_number: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            ASN: An instance of the ASN class.
        """
        indicator_obj = ASN(as_number, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def campaign(self, name: str, **kwargs) -> Campaign:
        """Add Campaign data to Batch.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            first_seen (str, kwargs): The first seen datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Campaign: An instance of the Campaign class.
        """
        group_obj = Campaign(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def cidr(self, block: str, **kwargs) -> CIDR:
        """Add CIDR data to Batch.

        Args:
            block: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            CIDR: An instance of the CIDR class.
        """
        indicator_obj = CIDR(block, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def close(self):
        """Cleanup batch job."""
        self.dump()

        # cleanup shelf files
        try:
            self.groups_shelf.close()
            os.unlink(self.group_shelf_fqfn)
        except Exception as ex:
            self.log.warning(f'action=batch-close, filename={self.group_shelf_fqfn} exception={ex}')

        # cleanup shelf files
        try:
            self.indicators_shelf.close()
            os.unlink(self.indicator_shelf_fqfn)
        except Exception as ex:
            self.log.warning(
                f'action=batch-close, filename={self.indicator_shelf_fqfn} exception={ex}'
            )

    def course_of_action(self, name: str, **kwargs) -> CourseOfAction:
        """Add Course Of Action Pattern data to Batch object.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            CourseOfAction: An instance of the CourseOfAction class.
        """
        group_obj = CourseOfAction(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    @property
    def data(self) -> dict:
        """Return the batch indicator/group and file data to be sent to the ThreatConnect API.

        **Processing Order:**
        * Process groups in memory up to max batch size.
        * Process groups in shelf to max batch size.
        * Process indicators in memory up to max batch size.
        * Process indicators in shelf up to max batch size.

        This method will remove the group/indicator from memory and/or shelf.

        Returns:
            dict: A dictionary of group, indicators, and/or file data.
        """
        data = {'file': {}, 'group': [], 'indicator': []}
        tracker = {'count': 0}

        # process group from memory, returning if max values have been reached
        if self.data_groups(data, self.groups, tracker) is True:
            return data

        # process group from shelf file, returning if max values have been reached
        if self.data_groups(data, self.groups_shelf, tracker) is True:
            return data

        # process indicator from memory, returning if max values have been reached
        if self.data_indicators(data, self.indicators, tracker) is True:
            return data

        # process indicator from shelf file, returning if max values have been reached
        if self.data_indicators(data, self.indicators_shelf, tracker) is True:
            return data

        return data

    def data_group_association(self, data: dict, tracker: dict, xid: str):
        """Return group dict array following all associations.

        The *data* dict is passed by reference to make it easier to update both the group data
        and file data inline versus passing the data all the way back up to the calling methods.

        Args:
            data: The data dict to update with group and file data.
            tracker: A dict containing total count of all entities collected.
            xid: The xid of the group to retrieve associations.
        """
        xids = deque()
        xids.append(xid)

        while xids:
            xid = xids.popleft()  # remove current xid
            group_data = None

            if xid in self.groups:
                group_data = self.groups.get(xid)
                del self.groups[xid]
            elif xid in self.groups_shelf:
                group_data = self.groups_shelf.get(xid)
                del self.groups_shelf[xid]

            if group_data:
                file_data, group_data = self.data_group_type(group_data)
                data['group'].append(group_data)
                if file_data:
                    data['file'][xid] = file_data

                # update entity trackers
                tracker['count'] += 1

                # extend xids with any groups associated with the same GroupType
                xids.extend(group_data.get('associatedGroupXid', []))

    @staticmethod
    def data_group_type(group_data: dict | GroupType) -> tuple[dict, dict]:
        """Return dict representation of group data and file data.

        Args:
            group_data: The group data.

        Returns:
            Tuple[dict, dict]: A tuple containing file_data and group_data.
        """
        file_data = {}
        if isinstance(group_data, dict):
            # process file content
            file_content = group_data.pop('fileContent', None)
            if file_content is not None:
                file_data = {
                    'fileContent': file_content,
                    'fileName': group_data.get('fileName'),
                    'type': group_data.get('type'),
                }
        else:
            # get the file data from the GroupType and return dict format of GroupType
            if group_data.data.get('type') in ['Document', 'Report']:
                file_data = group_data.file_data
            group_data = group_data.data

        return file_data, group_data

    def data_groups(self, data: dict, groups: dict | shelve.Shelf[Any], tracker: dict) -> bool:
        """Process Group data.

        Args:
            data: The data dict to update with group and file data.
            groups: The list of groups to process.
            tracker: A dict containing total count of all entities collected.

        Returns:
            bool: True if max values have been hit, else False.
        """
        # convert groups.keys() to a list to prevent dictionary change error caused by
        # the data_group_association function deleting items from the GroupType.

        # process the group
        for xid in list(groups.keys()):
            # get association from group data
            self.data_group_association(data, tracker, xid)

            if tracker['count'] % 10_000 == 0:
                # log count/size at a sane level
                self.log.debug(
                    '''feature=batch, action=data-groups, ''' f'''count={tracker.get('count'):,}'''
                )

        return False

    def data_indicators(
        self, data: dict, indicators: dict | shelve.Shelf[Any], tracker: dict
    ) -> bool:
        """Process Indicator data.

        Args:
            data: The data dict to update with group and file data.
            indicators: The list of indicators to process.
            tracker: A dict containing total count of all entities collected.

        Returns:
            bool: True if max values have been hit, else False.
        """
        # process the indicator
        for xid, indicator_data in list(indicators.items()):
            if not isinstance(indicator_data, dict):
                indicator_data = indicator_data.data
            data['indicator'].append(indicator_data)
            del indicators[xid]

            # update entity trackers
            tracker['count'] += 1

            if tracker['count'] % 10_000 == 0:
                # log count/size at a sane level
                self.log.debug(
                    '''feature=batch, action=data-indicators, '''
                    f'''count={tracker.get('count'):,}'''
                )

        return False

    def document(self, name: str, file_name: str, **kwargs) -> Document:
        """Add Document data to Batch.

        Args:
            name: The name for this Group.
            file_name: The name for the attached file for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_content (str;method, kwargs): The file contents or
                callback method to retrieve file content.
            malware (bool, kwargs): If true the file is considered malware.
            password (bool, kwargs): If malware is true a password for the zip archive is
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Document: An instance of the Document class.
        """
        group_obj = Document(name, file_name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def dump(self):
        """Process Batch request to ThreatConnect API."""
        content = self.data
        content.pop('file', {})
        if not content.get('group') and not content.get('indicator'):
            return

        # special code for debugging App using batchV2.
        self.write_batch_json(content)

        # store the length of the batch data to use for poll interval calculations
        self.log.info(
            '''feature=batch, event=dump, type=group, ''' f'''count={len(content['group']):,}'''
        )
        self.log.info(
            '''feature=batch, event=dump, type=indicator, '''
            f'''count={len(content['indicator']):,}'''
        )
        self.log.info(f'''feature=batch, event=dump, type=batch, size={self._batch_size:,}''')

        # reset batch size after dump
        self._batch_size = 0

    def email(self, name: str, subject: str, header: str, body: str, **kwargs) -> Email:
        """Add Email data to Batch.

        Args:
            name: The name for this Group.
            subject: The subject for this Email.
            header: The header for this Email.
            body: The body for this Email.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            from_addr (str, kwargs): The **from** address for this Email.
            to_addr (str, kwargs): The **to** address for this Email.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Email: An instance of the Email class.
        """
        group_obj = Email(name, subject, header, body, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def email_address(self, address: str, **kwargs) -> EmailAddress:
        """Add Email Address data to Batch.

        Args:
            address: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            EmailAddress: An instance of the EmailAddress class.
        """
        indicator_obj = EmailAddress(address, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def event(self, name: str, **kwargs) -> Event:
        """Add Event data to Batch.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Event: An instance of the Event class.
        """
        group_obj = Event(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def file(
        self,
        md5: str | None = None,
        sha1: str | None = None,
        sha256: str | None = None,
        **kwargs,
    ) -> File:
        """Add File data to Batch.

        .. note:: A least one file hash value must be specified.

        Args:
            md5: The md5 value for this Indicator.
            sha1: The sha1 value for this Indicator.
            sha256: The sha256 value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            size (str, kwargs): The file size for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            File: An instance of the File class.

        """
        indicator_obj = File(md5, sha1, sha256, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    @staticmethod
    def generate_xid(identifier: list | str | None = None) -> str:
        """Generate xid from provided identifiers.

        .. Important::  If no identifier is provided a unique xid will be returned, but it will
                        not be reproducible. If a list of identifiers are provided they must be
                        in the same order to generate a reproducible xid.

        Args:
            identifier:  Value(s) to be used to make a unique and reproducible xid.

        """
        if identifier is None:
            identifier = str(uuid.uuid4())
        elif isinstance(identifier, list):
            identifier = '-'.join([str(i) for i in identifier])
            # IMPORTANT: Do not remove this duplicate line or xids will change.
            identifier = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
        return hashlib.sha256(identifier.encode('utf-8')).hexdigest()

    def group(self, group_type: str, name: str, **kwargs) -> GroupType | dict:
        """Add Group data to Batch.

        Args:
            group_type: The ThreatConnect define Group type.
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            GroupType: An instance of one of the Group classes.
        """
        group_obj = Group(group_type, name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))

    @property
    def group_shelf_fqfn(self) -> str:
        """Return groups shelf fully qualified filename.

        For testing/debugging a previous shelf file can be copied into the tc_temp_path directory
        instead of creating a new shelf file.
        """
        if self._group_shelf_fqfn is None:
            # new shelf file
            self._group_shelf_fqfn = os.path.join(
                self.inputs.model.tc_temp_path, f'groups-{str(uuid.uuid4())}'
            )
        return self._group_shelf_fqfn

    @property
    def groups(self) -> dict:
        """Return dictionary of all Groups data."""
        if self._groups is None:
            self._groups = {}
        return self._groups

    @property
    def groups_shelf(self) -> shelve.Shelf[Any]:
        """Return dictionary of all Groups data."""
        if self._groups_shelf is None:
            self._groups_shelf = shelve.open(self.group_shelf_fqfn, writeback=False)  # nosec
        return self._groups_shelf

    def host(self, hostname: str, **kwargs) -> Host:
        """Add Host data to Batch.

        Args:
            hostname: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Host: An instance of the Host class.
        """
        indicator_obj = Host(hostname, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def incident(self, name: str, **kwargs) -> Incident:
        """Add Incident data to Batch.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Incident: An instance of the Incident class.
        """
        group_obj = Incident(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def indicator(self, indicator_type: str, summary: str, **kwargs) -> IndicatorType:
        """Add Indicator data to Batch.

        Args:
            indicator_type: The ThreatConnect define Indicator type.
            summary: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            IndicatorType: An instance of one of the Indicator classes.
        """
        indicator_obj = Indicator(indicator_type, summary, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    @property
    def indicator_shelf_fqfn(self) -> str:
        """Return indicator shelf fully qualified filename.

        For testing/debugging a previous shelf file can be copied into the tc_temp_path directory
        instead of creating a new shelf file.
        """
        if self._indicator_shelf_fqfn is None:
            # new shelf file
            self._indicator_shelf_fqfn = os.path.join(
                self.inputs.model.tc_temp_path, f'indicators-{str(uuid.uuid4())}'
            )
        return self._indicator_shelf_fqfn

    @property
    def indicators(self) -> dict:
        """Return dictionary of all Indicator data."""
        if self._indicators is None:
            # plain dict, but could be something else in future
            self._indicators = {}
        return self._indicators

    @property
    def indicators_shelf(self) -> shelve.Shelf[Any]:
        """Return dictionary of all Indicator data."""
        if self._indicators_shelf is None:
            self._indicators_shelf = shelve.open(  # nosec
                self.indicator_shelf_fqfn, writeback=False
            )
        return self._indicators_shelf

    def intrusion_set(self, name: str, **kwargs) -> IntrusionSet:
        """Add Intrusion Set data to Batch.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            IntrusionSet: An instance of the IntrusionSet class.
        """
        group_obj = IntrusionSet(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def malware(self, name: str, **kwargs) -> Malware:
        """Add Malware data to Batch object.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Malware: An instance of the Malware class.
        """
        group_obj = Malware(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def mutex(self, mutex: str, **kwargs) -> Mutex:
        """Add Mutex data to Batch.

        Args:
            mutex: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Mutex: An instance of the Mutex class.
        """
        indicator_obj = Mutex(mutex, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def registry_key(
        self, key_name: str, value_name: str, value_type: str, **kwargs
    ) -> RegistryKey:
        """Add Registry Key data to Batch.

        Args:
            key_name: The key_name value for this Indicator.
            value_name: The value_name value for this Indicator.
            value_type: The value_type value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            RegistryKey: An instance of the Registry Key class.
        """
        indicator_obj = RegistryKey(key_name, value_name, value_type, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def report(self, name: str, **kwargs) -> Report:
        """Add Report data to Batch.

        Args:
            name: The name for this Group.
            file_name (str): The name for the attached file for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                file content.
            publish_date (str, kwargs): The publish datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Report: An instance of the Report class.
        """
        group_obj = Report(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def save(self, resource: dict | GroupType | IndicatorType):
        """Save group|indicator dict, GroupType, or IndicatorTypes to shelve.

        Best effort to save group/indicator data to disk.  If for any reason the save fails
        the data will still be accessible from list in memory.

        Args:
            resource: The Group or Indicator data.
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

            if resource_type in self.tic.group_types:
                try:
                    # groups
                    self.groups_shelf[xid] = resource
                except Exception:
                    saved = False

                if saved:
                    try:
                        del self.groups[xid]
                    except KeyError:
                        # if group was saved twice it would already be delete
                        pass
            elif resource_type in self.tic.indicator_types_data:
                try:
                    # indicators
                    self.indicators_shelf[xid] = resource
                except Exception:
                    saved = False

                if saved:
                    try:
                        del self.indicators[xid]
                    except KeyError:
                        # if indicator was saved twice it would already be delete
                        pass

    def signature(
        self, name: str, file_name: str, file_type: str, file_text: str, **kwargs
    ) -> Signature:
        """Add Signature data to Batch.

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
            name: The name for this Group.
            file_name: The name for the attached signature for this Group.
            file_type: The signature type for this Group.
            file_text: The signature content for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Signature: An instance of the Signature class.
        """
        group_obj = Signature(name, file_name, file_type, file_text, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def tactic(self, name: str, **kwargs) -> Tactic:
        """Add Tactic data to Batch object.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Tactic: An instance of the Tactic class.
        """
        group_obj = Tactic(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def threat(self, name: str, **kwargs) -> Threat:
        """Add Threat data to Batch.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Threat: An instance of the Threat class.
        """
        group_obj = Threat(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def tool(self, name: str, **kwargs) -> Tool:
        """Add Tool data to Batch object.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            Tool: An instance of the Tool class.
        """
        group_obj = Tool(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def user_agent(self, text: str, **kwargs) -> UserAgent:
        """Add User Agent data to Batch.

        Args:
            text: The value for this Indicator.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.
            **kwargs: Additional keyword arguments.

        Returns:
            UserAgent: An instance of the UserAgent class.
        """
        indicator_obj = UserAgent(text, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def url(self, text: str, **kwargs) -> URL:
        """Add URL Address data to Batch.

        Args:
            text: The value for this Indicator.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.

        Returns:
            URL: An instance of the URL class.
        """
        indicator_obj = URL(text, **kwargs)
        return self._indicator(indicator_obj, kwargs.get('store', True))  # type: ignore

    def vulnerability(self, name: str, **kwargs) -> Vulnerability:
        """Add Vulnerability data to Batch.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
            store: (bool, kwargs): Advanced - Defaults to True. If True
                the indicator data will be stored in instance list.

        Returns:
            Vulnerability: An instance of the Vulnerability class.
        """
        group_obj = Vulnerability(name, **kwargs)
        return self._group(group_obj, kwargs.get('store', True))  # type: ignore

    def write_batch_json(self, content: dict):
        """Write batch json data to a file."""
        if content:
            # get timestamp as a string without decimal place and consistent length
            filename = f'{str(round(time.time() * 10000000))}.json.gz'
            if self.output_extension is not None:
                # add any additional extension provided
                filename += self.output_extension
            # TODO: is this needed
            self._batch_files.append(filename)
            fqfn = os.path.join(self.output_dir, filename)
            with gzip.open(fqfn, mode='wt', encoding='utf-8') as fh:
                json.dump(content, fh)

            # send callback the filename
            if callable(self.write_callback):
                self.write_callback(fqfn, **self.write_callback_kwargs)
