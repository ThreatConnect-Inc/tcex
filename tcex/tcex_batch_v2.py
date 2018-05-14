# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""
import hashlib
import json
import re
import time
import uuid

# import local modules for dynamic reference
module = __import__(__name__)

# TODO: Add auto submit feature?

def custom_indicator_class_factory(indicator_type, base_class, class_dict, value_count):
    """Internal method for dynamically building Custom Indicator Class"""
    def init_1(self, tcex, value1, rating=None, confidence=None, xid=True):
        """Init method for Custom Indicator Types with one value"""
        summary = self.build_summary(value1)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, rating, confidence, xid)
        self._indicator_data['value1'] = value1
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_2(self, tcex, value1, value2, rating=None, confidence=None, xid=True):
        """Init method for Custom Indicator Types with two values"""
        summary = self.build_summary(value1, value2)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, rating, confidence, xid)
        self._indicator_data['value1'] = value1
        self._indicator_data['value2'] = value2
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_3(self, tcex, value1, value2, value3, rating=None, confidence=None, xid=True):
        """Init method for Custom Indicator Types with three values"""
        summary = self.build_summary(value1, value2, value3)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, rating, confidence, xid)
        self._indicator_data['value1'] = value1
        self._indicator_data['value2'] = value2
        self._indicator_data['value3'] = value3
        for k, v in class_dict.items():
            setattr(self, k, v)

    class_name = indicator_type.replace(' ', '')
    init_method = locals()['init_{}'.format(value_count)]
    newclass = type(str(class_name), (base_class,), {"__init__": init_method})
    return newclass


class Batch(object):
    """ThreatConnect Batch Import Module"""

    def __init__(self, tcex, owner, action=None, attribute_write_type=None, halt_on_error=False):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            tcex: Instance of TcEx
            owner: The ThreatConnect owner for Batch action.
            action: Action for the batch job ['Create', 'Delete'].
            attribute_write_type: Write type for Indicator attributes ['Append', 'Replace'].
            halt_on_error: Flag to indicate that the batch job should halt on error.
        """
        self.tcex = tcex
        self._owner = owner
        self._action = action or 'Create'
        self._attribute_write_type = attribute_write_type or 'Replace'
        self._halt_on_error = halt_on_error

        # default properties
        self._auto_submit = False
        self._auto_submit_limit = 10000
        self._poll_interval = 15
        self._poll_timeout = 3600

        # containers
        self._files = {}
        self._groups = set()
        self._groups_by_id = {}
        self._groups_raw = []
        self._indicators = []
        self._indicators_raw = []

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
        """Generate Custom Indicator Classes"""

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
            custom_class = custom_indicator_class_factory(name, Indicator, class_data, value_count)
            setattr(module, class_name, custom_class)

            # Add Custom Indicator Method
            self._gen_indicator_method(name, custom_class, value_count)

    def _gen_indicator_method(self, name, custom_class, value_count):
        """Generate Custom Indicator Methods"""
        method_name = name.replace(' ', '_').lower()

        # Add Method for each Custom Indicator class
        def method_1(value1, rating=None, confidence=None, xid=True):
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(self.tcex, value1, rating, confidence, xid)
            self._indicators.append(indicator_obj)
            return indicator_obj

        def method_2(value1, value2, rating=None, confidence=None, xid=True):
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(self.tcex, value1, value2, rating, confidence, xid)
            self._indicators.append(indicator_obj)
            return indicator_obj

        def method_3(value1, value2, value3, rating=None, confidence=None, xid=True):
            """Add Custom Indicator data to Batch object"""
            indicator_obj = custom_class(
                self.tcex, value1, value2, value3, rating, confidence, xid)
            self._indicators.append(indicator_obj)
            return indicator_obj

        method = locals()['method_{}'.format(value_count)]
        setattr(self, method_name, method)

    def _group_lookup(self, xid, group_obj):
        """magic"""
        if not isinstance(xid, bool):
            if self._groups_by_id.get(xid) is not None:
                group_obj = self._groups_by_id.get(xid)
            else:
                self._groups_by_id[xid] = group_obj
        return group_obj

    @staticmethod
    def _indicator_values(indicator):
        """Process indicators expanding file hashes/custom indicators into multiple entries

        .. note:: remove first_indicator logic.

        Args:
            indicator (string): " : " delimited string
        Returns:
            (list): a list of indicators split on " : ".
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
        """Return batch action"""
        return self._action

    @action.setter
    def action(self, action):
        """Set batch action"""
        self._action = action

    def add_group(self, group_data):
        """Add a group to Batch Job

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
            group_data (dict): Full Group data including attributes, labels, tags, and associations.
        """
        file_content = group_data.pop('fileContent', None)
        if file_content is not None:
            self._files[group_data.get('xid')] = {
                'fileContent': file_content,
                'type': group_data.get('type')
            }
        self._groups_raw.append(group_data)

    def add_indicator(self, indicator_data):
        """Add an indicator to Batch Job

        {
            "type": "File",
            "rating": 5.00,
            "confidence": 50,
            "summary": "53c3609411c83f363e051d455ade78a7 : 57a49b478310e4313c54c0fee46e4d70a73dd580
             : db31cb2a748b7e0046d8c97a32a7eb4efde32a0593e5dbd58e07a3b4ae6bf3d7",
            "associatedGroupXid": [
                "e336e2dd-5dfb-48cd-a33a-f8809e83e904",
            ],
            "attribute": [{
                "type": "Source",
                "displayed": true,
                "value": "Malware Analysis provided by external AMA."
            }],
            "fileOccurrence": [{
                "fileName": "drop1.exe",
                "path": "C:\\test\\",
                "date": "2017-03-03T18:00:00-06:00"
            }],
            "tag": [{
                "name": "China"
            }],
            "xid": "e336e2dd-5dfb-48cd-a33a-f8809e83e904:170139"
        }

        Args:
            indicator_data (dict): Full Indicator data including attributes, labels, tags,
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
        self._indicators_raw.append(indicator_data)

    def address(self, ip, rating=None, confidence=None, xid=True):
        """Add Address data to Batch object"""
        indicator_obj = Address(self.tcex, ip, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def adversary(self, name, xid=True):
        """Add Adversary data to Batch object"""
        group_obj = Adversary(self.tcex, name, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def asn(self, as_number, rating=None, confidence=None, xid=True):
        """Add ASN data to Batch object"""
        indicator_obj = ASN(self.tcex, as_number, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    @property
    def attribute_write_type(self):
        """Return batch attribute write type"""
        return self._attribute_write_type

    @attribute_write_type.setter
    def attribute_write_type(self, attribute_write_type):
        """Set batch attribute write type"""
        self._attribute_write_type = attribute_write_type

    @property
    def auto_submit(self):
        """Return batch auto submit setting"""
        return self._auto_submit

    @auto_submit.setter
    def auto_submit(self, auto_submit):
        """Set batch auto submit setting"""
        self._auto_submit = self.tcex.utils.to_bool(auto_submit)

    @property
    def auto_submit_limit(self):
        """Return batch auto submit limit"""
        return self._auto_submit_limit

    @auto_submit_limit.setter
    def auto_submit_limit(self, limit):
        """Set batch auto submit limit"""
        self._auto_submit_limit = int(limit)

    def campaign(self, name, first_seen=None, xid=True):
        """Add Campaign data to Batch object"""
        group_obj = Campaign(self.tcex, name, first_seen, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def cidr(self, block, rating=None, confidence=None, xid=True):
        """Add CIDR data to Batch object"""
        indicator_obj = CIDR(self.tcex, block, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    @property
    def data(self):
        """Return the batch data to be sent to the ThreatConnect API"""
        # process group objects
        for group_data in self._groups:
            self._groups_raw.append(group_data.data)
            if group_data.data.get('type') in ['Document', 'Report']:
                self._files[group_data.data.get('xid')] = group_data.file_data
        # process indicator objects
        for indicator in self._indicators:
            self._indicators_raw.append(indicator.data)
        # clear data from lists
        self._groups = []
        self._indicators = []
        return {
            'group': self._groups_raw,
            'indicator': self._indicators_raw
        }

    def document(self, name, file_name, file_content=None, malware=False, password=None, xid=True):
        """Add Document data to Batch object"""
        group_obj = Document(self.tcex, name, file_name, file_content, malware, password, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def email(self, name, subject, header, body, to_addr=None, from_addr=None, xid=True):
        """Add Email data to Batch object"""
        group_obj = Email(self.tcex, name, subject, header, body, to_addr, from_addr, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def email_address(self, address, rating=None, confidence=None, xid=True):
        """Add Email Address data to Batch object"""
        indicator_obj = EmailAddress(self.tcex, address, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def errors(self, batch_id):
        """Retrieve Batch errors to ThreatConnect API

        [{
            "errorReason": "Incident incident-001 has an invalid status.",
            "errorSource": "incident-001 is not valid."
        }, {
            "errorReason": "Incident incident-002 has an invalid status.",
            "errorSource":"incident-002 is not valid."
        }]

        """
        errors = []
        try:
            r = self.tcex.session.get('/v2/batch/{}/errors'.format(batch_id))
            # if r.status_code == 404:
            #     time.sleep(5)  # allow time for errors to be processed
            #     r = self.tcex.session.get('/v2/batch/{}/errors'.format(batch_id))
            self.tcex.log.debug('Retrieve Errors for ID {}: status code {}, errors {}'.format(
                batch_id, r.status_code, r.text))
            self.tcex.log.debug('Retrieve Errors URL {}'.format(r.url))
            if r.ok:
                errors = json.loads(r.text)
            # temporarily process errors to find "critical" errors.
            # FR in core to return error codes.
            for error in errors:
                error_reason = error.get('errorReason')
                for error_msg in self._critical_failures:
                    if re.findall(error_msg, error_reason):
                        self.tcex.raise_error(1500, [error_reason])
            return errors
        except Exception as e:
            self.tcex.raise_error(560, [e])

    def event(self, name, event_date=None, status=None, xid=True):
        """Add Event data to Batch object"""
        group_obj = Event(self.tcex, name, event_date, status, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def file(self, md5=None, sha1=None, sha256=None, size=None, rating=None, confidence=None,
             xid=True):
        """Add File data to Batch object"""
        indicator_obj = File(self.tcex, md5, sha1, sha256, size, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def group(self, group_type, name, xid=True):
        """Add Group data to Batch object"""
        group_type = group_type.replace(' ', '')
        group_obj = Group(self.tcex, group_type, name, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    @property
    def halt_on_error(self):
        """Return batch halt_on_error"""
        return self._halt_on_error

    @halt_on_error.setter
    def halt_on_error(self, halt_on_error):
        """Set batch halt_on_error"""
        self._halt_on_error = halt_on_error

    def host(self, hostname, rating=None, confidence=None, xid=True):
        """Add Email Address data to Batch object"""
        indicator_obj = Host(self.tcex, hostname, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def incident(self, name, event_date=None, status=None, xid=True):
        """Add Incident data to Batch object"""
        group_obj = Incident(self.tcex, name, event_date, status, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def indicator(self, indicator_type, summary, rating=None, confidence=None, xid=True):
        """Add Indicator data to Batch object"""
        indicator_type = indicator_type.replace(' ', '')
        indicator_obj = Indicator(self.tcex, indicator_type, summary, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def intrusion_set(self, name, xid=True):
        """Add Intrusion Set data to Batch object"""
        group_obj = IntrusionSet(self.tcex, name, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def mutex(self, mutex, rating=None, confidence=None, xid=True):
        """Add Mutex data to Batch object"""
        indicator_obj = Mutex(self.tcex, mutex, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def poll(self, batch_id, interval=None, timeout=None):
        """Poll Batch status to ThreatConnect API

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
            batch_id (str): The ID of the current batch job.
            interval (int): Number of seconds to delay between each status request.
            timeout (int): The number of seconds before the poll should timeout.
        Returns:
            (dict): The batch status returned from the API.

        """
        if interval is None:
            interval = self.poll_interval
        else:
            interval = int(interval)
        if timeout is None:
            timeout = self.poll_timeout
        else:
            timeout = int(timeout)

        poll_time = 0
        data = {}
        while True:
            try:
                r = self.tcex.session.get('/v2/batch/{}'.format(batch_id))
                if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
                    self.tcex.raise_error(545, [r.status_code, r.text])
                data = r.json()
                if data.get('status') != 'Success':
                    self.tcex.raise_error(545, [r.status_code, r.text])
                if data.get('data', {}).get('batchStatus', {}).get('status') == 'Completed':
                    self.tcex.log.debug('Batch Status: {}'.format(data))
                    return data
                time.sleep(interval)
            except Exception as e:
                self.tcex.raise_error(540, [e])
            # time out poll to prevent App running indefinitely
            if poll_time >= timeout:
                self.tcex.log.info(
                    'Status check has reached the timeout value ({} seconds).'.format(timeout))
                return data
            poll_time += interval
            self.tcex.log.debug('Batch poll time: {} seconds'.format(poll_time))

    @property
    def poll_interval(self):
        """Return current poll interval value"""
        return self._poll_interval

    @poll_interval.setter
    def poll_interval(self, interval):
        """Set the poll interval value"""
        self._poll_interval = int(interval)

    @property
    def poll_timeout(self):
        """Return current poll timeout value"""
        return self._poll_timeout

    @poll_timeout.setter
    def poll_timeout(self, seconds):
        """Set the poll timeout value"""
        self._poll_timeout = int(seconds)

    def registry_key(self, key_name, value_name, value_type, rating=None, confidence=None,
                     xid=True):
        """Add Registry Key data to Batch object"""
        indicator_obj = RegistryKey(
            self.tcex, key_name, value_name, value_type, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def report(self, name, file_name, file_content=None, publish_date=None, xid=True):
        """Add Report data to Batch object"""
        group_obj = Report(self.tcex, name, file_name, file_content, publish_date, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    @property
    def settings(self):
        """Return batch job settings"""
        return {
            'action': self._action,
            # not supported in v2 batch
            # 'attributeWriteType': self._attribute_write_type,
            'attributeWriteType': 'Replace',
            'haltOnError': self._halt_on_error,
            'owner': self._owner,
            'version': 'V2'
        }

    def signature(self, name, file_name, file_type, file_text, xid=True):
        """Add Signature data to Batch object"""
        group_obj = Signature(self.tcex, name, file_name, file_type, file_text, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def submit(self, submit_data=True, poll=True, errors=False):
        """Send the batch request to ThreatConnect

        Args:
            submit_data (boolean): Submit the data after the job request.
            poll (boolean): Poll for status.
            errors (boolean): Retrieve and batch errors.
        Returns:
            (dict): Batch data including batch id and batch status.
        """
        batch_data = {}
        batch_data['batch_id'] = self.submit_job()
        if submit_data:
            self.submit_data(batch_data.get('batch_id'))
            if poll:
                # set an initial delay to allow small batch jobs to finish without a poll delay
                time.sleep(3)
                batch_data['batch_status'] = self.poll(batch_data.get('batch_id'))
                # retrieve errors
                if errors:
                    data = batch_data.get('batch_status').get('data', {})
                    if data.get('batchStatus', {}).get('errorCount', 0) > 0:
                        batch_data['errors'] = self.errors(batch_data.get('batch_id'))
        if submit_data:
            # submit file data after batch job is complete
            self.submit_files()
        return batch_data

    def submit_data(self, batch_id):
        """Submit Batch request to ThreatConnect API

        Args:
            batch_id (string): The batch id of the current job.
        """
        headers = {'Content-Type': 'application/octet-stream'}
        try:
            r = self.tcex.session.post(
                '/v2/batch/{}'.format(batch_id), headers=headers, json=self.data)
        except Exception as e:
            self.tcex.raise_error(1520, [e])
        if not r.ok:
            self.tcex.raise_error(1525, [r.status_code, r.text])
        # reset values
        self._groups_raw = []
        self._indicators_raw = []

    def submit_files(self):
        """Submit File Content for Documents and Reports to ThreatConnect API"""
        # TODO: track file submission
        # file_status = []
        for xid, content_data in self._files.items():
            content = content_data.get('fileContent')
            if content is None:
                self.tcex.log.warning('File content was null for xid {}.'.format(xid))
                continue
            if callable(content):
                content = content_data.get('fileContent')(xid)
            if content_data.get('type') == 'Document':
                api_branch = 'documents'
            elif content_data.get('type') == 'Report':
                api_branch = 'reports'

            # Post File
            url = '/v2/groups/{}/{}/upload'.format(api_branch, xid)
            headers = {'Content-Type': 'application/octet-stream'}
            try:
                r = self.tcex.session.post(url, data=content.encode('utf-8'), headers=headers)
                if r.status_code == 401:
                    # update file if already exists
                    self.tcex.log.info('Received 401 status code using POST. Trying PUT to update.')
                    r = self.tcex.session.put(url, data=content.encode('utf-8'), headers=headers)
                self.tcex.log.debug('{} Upload URL: {}.'.format(content_data.get('type'), r.url))
                self.tcex.log.info('Status {} for file upload with xid {}.'.format(
                    r.status_code, xid))
            # except UnicodeDecodeError:
            #     r = self.tcex.session.post(url, data=content.encode('utf-8'), headers=headers)
            except Exception as e:
                self.tcex.raise_error(580, [e])
            if not r.ok:
                self.tcex.raise_error(585, [r.status_code, r.text])
        # reset files
        self._files = {}

    def submit_job(self):
        """Submit Batch request to ThreatConnect API"""
        try:
            r = self.tcex.session.post('/v2/batch', json=self.settings)
        except Exception as e:
            self.tcex.raise_error(1505, [e])
        if not r.ok or 'application/json' not in r.headers.get('content-type', ''):
            self.tcex.raise_error(1510, [r.status_code, r.text])
        data = r.json()
        if data.get('status') != 'Success':
            self.tcex.raise_error(1510, [r.status_code, r.text])
        self.tcex.log.debug('Batch Submit Data: {}'.format(data))
        return data.get('data', {}).get('batchId')

    def threat(self, name, xid=True):
        """Add Threat data to Batch object"""
        group_obj = Threat(self.tcex, name, xid)
        group_obj = self._group_lookup(xid, group_obj)
        self._groups.add(group_obj)
        return group_obj

    def user_agent(self, text, rating=None, confidence=None, xid=True):
        """Add User Agent data to Batch object"""
        indicator_obj = UserAgent(self.tcex, text, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def url(self, text, rating=None, confidence=None, xid=True):
        """Add URL Address data to Batch object"""
        indicator_obj = URL(self.tcex, text, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def __len__(self):
        """Return the number of groups and indicators"""
        group_len = len(self._groups) + len(self._groups_raw)
        indicator_len = len(self._indicators) + len(self._indicators_raw)
        return group_len + indicator_len

    def __str__(self):
        """Send the batch request to ThreatConnect"""
        return json.dumps(self.data, indent=4, sort_keys=True)


#
# Groups
#


class Group(object):
    """ThreatConnect Batch Group Object"""

    def __init__(self, tcex, group_type, name, xid):
        """Initialize Class Properties"""
        self.tcex = tcex
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

    def _xid(self, xid):
        """Return a valid xid"""
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
        """Add custom field to Group object"""
        self._group_data[key] = value

    def association(self, group_xid):
        """Add association using xid value"""
        self._group_data.setdefault('associatedGroupXid', []).append(group_xid)

    def attribute(self, attr_type, attr_value, displayed=None, source=None, formatter=None):
        """Return instance of Attribute"""
        attr = Attribute(self.tcex, attr_type, attr_value, displayed, source, formatter)
        self._attributes.append(attr)
        return attr

    @property
    def data(self):
        """Return Group data"""
        # add attributes
        if self._attributes:
            self._group_data['attribute'] = []
            for attr in self._attributes:
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
                self._group_data['tag'].append(tag.data)
        return self._group_data

    @property
    def name(self):
        """Return Group name"""
        return self._group_data.get('name')

    def security_label(self, name, description=None, color=None):
        """Return instance of Tag"""
        label = SecurityLabel(self.tcex, name, description, color)
        self._labels.append(label)
        return label

    def tag(self, name, formatter=None):
        """Return instance of Tag"""
        tag = Tag(self.tcex, name, formatter)
        self._tags.append(tag)
        return tag

    @property
    def xid(self):
        """Return Group xid"""
        return self._group_data.get('xid')

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class Adversary(Group):
    """ThreatConnect Batch Adversary Object"""

    def __init__(self, tcex, name, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
        """
        super(Adversary, self).__init__(tcex, 'Adversary', name, xid)


class Campaign(Group):
    """ThreatConnect Batch Campaign Object"""

    def __init__(self, tcex, name, first_seen=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            first_seen (string): The date of the campaign was first seen
                                 (date will be auto-formatted).
        """
        super(Campaign, self).__init__(tcex, 'Campaign', name, xid)
        if first_seen is not None:
            self._group_data['firstSeen'] = self.tcex.utils.format_datetime(
                first_seen, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def first_seen(self):
        """Return Document first seen"""
        return self._group_data.get('firstSeen')

    @first_seen.setter
    def first_seen(self, first_seen):
        """Set Document first seen"""
        self._group_data['firstSeen'] = self.tcex.utils.format_datetime(
            first_seen, date_format='%Y-%m-%dT%H:%M:%SZ')


class Document(Group):
    """ThreatConnect Batch Document Object"""

    def __init__(self, tcex, name, file_name, file_content=None, malware=False, password=None,
                 xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            file_name (string): The name of the attached document.
            file_content (bytes|method): The file content or method to call to return content.
            malware (boolean): Indicates the attached document is malware.
        """
        super(Document, self).__init__(tcex, 'Document', name, xid)
        self._group_data['fileName'] = file_name
        self._file_data = {'type': self._group_data.get('type')}
        self._file_data['fileContent'] = file_content
        if malware:
            self._group_data['malware'] = malware
        if password is not None:
            self._group_data['password'] = password

    @property
    def file_content(self):
        """Return Group files"""
        return self._file_data.get('fileContent')

    @file_content.setter
    def file_content(self, file_content):
        """Set Document or Report file data"""
        self._file_data['fileContent'] = file_content

    @property
    def file_data(self):
        """Return Group files"""
        return self._file_data

    @property
    def malware(self):
        """Return Document malware"""
        return self._group_data.get('malware', False)

    @malware.setter
    def malware(self, malware):
        """Set Document malware"""
        self._group_data['malware'] = malware

    @property
    def password(self):
        """Return Document password"""
        return self._group_data.get('password', False)

    @password.setter
    def password(self, password):
        """Set Document password"""
        self._group_data['password'] = password


class Email(Group):
    """ThreatConnect Batch Email Object"""

    def __init__(self, tcex, name, subject, header, body, to_addr=None, from_addr=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            subject (string): The Email subject.
            header (string): The Email header.
            body (string): The Email body.
            to_addr (string): The Email **to** address.
            from_addr (string): The Email **from** address.
        """
        super(Email, self).__init__(tcex, 'Email', name, xid)
        self._group_data['subject'] = subject
        self._group_data['header'] = header
        self._group_data['body'] = body
        if to_addr is not None:
            self._group_data['to'] = to_addr
        if from_addr is not None:
            self._group_data['from'] = from_addr

    @property
    def from_addr(self):
        """Return Email to"""
        return self._group_data.get('to')

    @from_addr.setter
    def from_addr(self, from_addr):
        """Set Email from"""
        self._group_data['from'] = from_addr

    @property
    def to_addr(self):
        """Return Email to"""
        return self._group_data.get('to')

    @to_addr.setter
    def to_addr(self, to_addr):
        """Set Email to"""
        self._group_data['to'] = to_addr


class Event(Group):
    """ThreatConnect Batch Event Object"""

    def __init__(self, tcex, name, event_date=None, status=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            event_date (string): The date of the Event (date will be auto-formatted).
        """
        super(Event, self).__init__(tcex, 'Event', name, xid)
        if event_date is not None:
            self._group_data['eventDate'] = self.tcex.utils.format_datetime(
                event_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        if status is not None:
            self._group_data['status'] = status

    @property
    def first_seen(self):
        """Return Document first seen"""
        return self._group_data.get('firstSeen')

    @first_seen.setter
    def first_seen(self, first_seen):
        """Set Document first seen"""
        self._group_data['firstSeen'] = self.tcex.utils.format_datetime(
            first_seen, date_format='%Y-%m-%dT%H:%M:%SZ')


class Incident(Group):
    """ThreatConnect Batch Incident Object"""

    def __init__(self, tcex, name, event_date=None, status=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            event_date (string): The date of the event (date will be auto-formatted).
            status (string): The status of the Incident.
        """
        super(Incident, self).__init__(tcex, 'Incident', name, xid)
        if event_date is not None:
            self._group_data['eventDate'] = self.tcex.utils.format_datetime(
                event_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        if status is not None:
            self._group_data['status'] = status

    @property
    def event_date(self):
        """Return Incident event date"""
        return self._group_data.get('eventDate')

    @event_date.setter
    def event_date(self, event_date):
        """Set Incident event_date"""
        self._group_data['eventDate'] = self.tcex.utils.format_datetime(
            event_date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def status(self):
        """Return Incident status"""
        return self._group_data.get('status')

    @status.setter
    def status(self, status):
        """Set Incident status

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

    def __init__(self, tcex, name, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
        """
        super(IntrusionSet, self).__init__(tcex, 'Intrusion Set', name, xid)


class Report(Group):
    """ThreatConnect Batch Report Object"""

    def __init__(self, tcex, name, file_name, file_content=None, publish_date=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            file_name (string): The name of the attached document.
            publish_date (string): The date the report was published (date will be auto-formatted).
        """
        super(Report, self).__init__(tcex, 'Report', name, xid)
        self._group_data['fileName'] = file_name
        self._file_data = {'type': self._group_data.get('type')}
        self._file_data['fileContent'] = file_content
        if publish_date is not None:
            self._group_data['publishDate'] = self.tcex.utils.format_datetime(
                publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def file_content(self):
        """Return Group files"""
        return self._file_data.get('fileContent')

    @file_content.setter
    def file_content(self, file_content):
        """Set Document or Report file data"""
        self._file_data['fileContent'] = file_content

    @property
    def file_data(self):
        """Return Group files"""
        return self._file_data

    @property
    def publish_date(self):
        """Return Report publish date"""
        return self._group_data.get('publishDate')

    @publish_date.setter
    def publish_date(self, publish_date):
        """Set Report publish date"""
        self._group_data['publishDate'] = self.tcex.utils.format_datetime(
            publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')


class Signature(Group):
    """ThreatConnect Batch Signature Object"""

    def __init__(self, tcex, name, file_name, file_type, file_text, xid=True):
        """Initialize Class Properties

        Valid file_types:
        + Snort ®
        + Suricata
        + YARA
        + ClamAV ®
        + OpenIOC
        + CybOX ™
        + Bro
        + Regex
        + SPL - Splunk® Search Processing Language

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            file_name (string): The Signature file name.
            file_type (string): The Signature file type.
            file_text (string): The Signature text.
        """
        super(Signature, self).__init__(tcex, 'Signature', name, xid)
        self._group_data['fileName'] = file_name
        self._group_data['fileType'] = file_type
        self._group_data['fileText'] = file_text
        # self._group_data['signatureDateAdded'] = self.tcex.utils.date_format()


class Threat(Group):
    """ThreatConnect Batch Threat Object"""

    def __init__(self, tcex, name, xid):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
        """
        super(Threat, self).__init__(tcex, 'Threat', name, xid)


#
# Indicators
#


class Indicator(object):
    """ThreatConnect Batch Indicator Object"""

    def __init__(self, tcex, indicator_type, summary, rating=None, confidence=None, xid=True):
        """Initialize Class Properties"""
        self.tcex = tcex
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

    def _xid(self, xid):
        """Return a valid xid"""
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
        """Add custom field to Indicator object"""

        if self._indicator_data.get('type') == 'File':
            if key == 'size':
                key = 'intValue1'
        if self._indicator_data.get('type') == 'Host':
            if key == 'dnsActive':
                key = 'flag1'
            elif key == 'whoisActive':
                key = 'flag2'
        self._indicator_data[key] = value

    def build_summary(self, val1=None, val2=None, val3=None):
        """Build the Indicator summary using available values"""
        summary = []
        if val1 is not None:
            summary.append(val1)
        if val2 is not None:
            summary.append(val2)
        if val3 is not None:
            summary.append(val3)
        if not summary:
            self.tcex.raise_error(590)
        return ' : '.join(summary)

    def association(self, group_xid):
        """Add association using xid value"""
        association = {'groupXid': group_xid}
        self._indicator_data.setdefault('associatedGroups', []).append(association)

    def attribute(self, attr_type, attr_value, displayed=None, source=None, formatter=None):
        """Return instance of Attribute"""
        attr = Attribute(self.tcex, attr_type, attr_value, displayed, source, formatter)
        self._attributes.append(attr)
        return attr

    @property
    def confidence(self):
        """Return Indicator confidence"""
        return self._indicator_data.get('confidence')

    @confidence.setter
    def confidence(self, confidence):
        """Set Indicator confidence"""
        self._indicator_data['confidence'] = int(confidence)

    @property
    def data(self):
        """Return Indicator data"""
        # add attributes
        if self._attributes:
            self._indicator_data['attribute'] = []
            for attr in self._attributes:
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
                self._indicator_data['tag'].append(tag.data)
        return self._indicator_data

    @property
    def private(self):
        """Return Indicator private"""
        return self._indicator_data.get('privateFlag')

    @private.setter
    def private(self, private):
        """Set Indicator private"""
        self._indicator_data['privateFlag'] = self.tcex.utils.to_bool(private)

    @property
    def rating(self):
        """Return Indicator rating"""
        return self._indicator_data.get('rating')

    @rating.setter
    def rating(self, rating):
        """Set Indicator rating"""
        self._indicator_data['rating'] = float(rating)

    @property
    def summary(self):
        """Return Indicator summary"""
        return self._indicator_data.get('summary')

    def security_label(self, name, description=None, color=None):
        """Return instance of Tag"""
        label = SecurityLabel(self.tcex, name, description, color)
        self._labels.append(label)
        return label

    def tag(self, name, formatter=None):
        """Return instance of Tag"""
        tag = Tag(self.tcex, name, formatter)
        self._tags.append(tag)
        return tag

    @property
    def xid(self):
        """Return Group xid"""
        return self._indicator_data.get('xid')

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class Address(Indicator):
    """ThreatConnect Batch Address Object"""

    def __init__(self, tcex, ip, rating=None, confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            ip (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(Address, self).__init__(tcex, 'Address', ip, rating, confidence, xid)


class ASN(Indicator):
    """ThreatConnect Batch ASN Object"""

    def __init__(self, tcex, as_number, rating=None, confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            as_number (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(ASN, self).__init__(tcex, 'ASN', as_number, rating, confidence, xid)
        self._indicator_data['value1'] = as_number


class CIDR(Indicator):
    """ThreatConnect Batch CIDR Object"""

    def __init__(self, tcex, block, rating=None, confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            block (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(CIDR, self).__init__(tcex, 'CIDR', block, rating, confidence, xid)
        self._indicator_data['value1'] = block


class EmailAddress(Indicator):
    """ThreatConnect Batch EmailAddress Object"""

    def __init__(self, tcex, address, rating=None, confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            address (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(EmailAddress, self).__init__(tcex, 'EmailAddress', address, rating, confidence, xid)


class File(Indicator):
    """ThreatConnect Batch File Object"""

    def __init__(self, tcex, md5=None, sha1=None, sha256=None, size=None, rating=None,
                 confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            md5 (string): The md5 value.
            sha1 (string): The sha1 value.
            sha256 (string): The sha256 value.
            size (string): The size of the file.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        self.tcex = tcex
        summary = self.build_summary(md5, sha1, sha256)  # build the indicator summary
        super(File, self).__init__(tcex, 'File', summary, rating, confidence, xid)
        self._indicator_data['type'] = 'File'
        if size is not None:
            self._indicator_data['intValue1'] = size
        # self._file_action = []

    def action(self, relationship):
        """Add a File Action"""
        action_obj = FileAction(self.tcex, self._indicator_data.get('xid'), relationship)
        self._file_actions.append(action_obj)
        return action_obj

    @property
    def md5(self):
        """Return Indicator md5"""
        return self._indicator_data.get('md5')

    @md5.setter
    def md5(self, md5):
        """Set Indicator md5"""
        self._indicator_data['md5'] = md5

    def occurrence(self, file_name=None, path=None, date=None):
        """Add a file Occurrence"""
        # self._indicator_data.setdefault('fileAction', {})
        # self._indicator_data['fileAction'].setdefault('fileData', {})
        occurrence_obj = FileOccurrence(self.tcex, file_name, path, date)
        self._occurrences.append(occurrence_obj)
        return occurrence_obj

    @property
    def sha1(self):
        """Return Indicator sha1"""
        return self._indicator_data.get('sha1')

    @sha1.setter
    def sha1(self, sha1):
        """Set Indicator sha1"""
        self._indicator_data['sha1'] = sha1

    @property
    def sha256(self):
        """Return Indicator sha256"""
        return self._indicator_data.get('sha256')

    @sha256.setter
    def sha256(self, sha256):
        """Set Indicator sha256"""
        self._indicator_data['sha256'] = sha256

    @property
    def size(self):
        """Return Indicator size"""
        return self._indicator_data.get('intValue1')

    @size.setter
    def size(self, size):
        """Set Indicator size"""
        self._indicator_data['intValue1'] = size


class Host(Indicator):
    """ThreatConnect Batch Host Object"""

    def __init__(self, tcex, hostname, dns_active=False, whois_active=False, rating=None,
                 confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            hostname (string): The Indicator value.
            dns_active (boolean): Enabled DNS tracking.
            whois_active (boolean): Enabled WhoIs tracking.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(Host, self).__init__(tcex, 'Host', hostname, rating, confidence, xid)
        if dns_active:
            self._indicator_data['flag1'] = dns_active
        if whois_active:
            self._indicator_data['flag2'] = dns_active

    @property
    def dns_active(self):
        """Return Indicator dns active"""
        return self._indicator_data.get('flag1')

    @dns_active.setter
    def dns_active(self, dns_active):
        """Set Indicator dns active"""
        self._indicator_data['flag1'] = dns_active

    @property
    def whois_active(self):
        """Return Indicator whois active"""
        return self._indicator_data.get('flag2')

    @whois_active.setter
    def whois_active(self, whois_active):
        """Set Indicator whois active"""
        self._indicator_data['flag2'] = whois_active


class Mutex(Indicator):
    """ThreatConnect Batch Mutex Object"""

    def __init__(self, tcex, mutex, rating=None, confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            mutex (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(Mutex, self).__init__(tcex, 'Mutex', mutex, rating, confidence, xid)
        self._indicator_data['value1'] = mutex


class RegistryKey(Indicator):
    """ThreatConnect Batch Registry Key Object"""

    def __init__(self, tcex, key_name, value_name, value_type, rating=None, confidence=None,
                 xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            key_name (string): The Registry Key name.
            value_name (string): The Registry Key value.
            value_type (string): The Registry Key value type.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        summary = self.build_summary(key_name, value_name, value_type)
        super(RegistryKey, self).__init__(tcex, 'Registry Key', summary, rating, confidence, xid)
        self._indicator_data['value1'] = key_name
        self._indicator_data['value2'] = value_name
        self._indicator_data['value3'] = value_type


class URL(Indicator):
    """ThreatConnect Batch URL Object"""

    def __init__(self, tcex, text, rating=None, confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            text (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(URL, self).__init__(tcex, 'URL', text, rating, confidence, xid)


class UserAgent(Indicator):
    """ThreatConnect Batch User Agent Object"""

    def __init__(self, tcex, text, rating=None, confidence=None, xid=True):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            text (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(UserAgent, self).__init__(tcex, 'User Agent', text, rating, confidence, xid)
        self._indicator_data['value1'] = text


#
# Metadata Classes
#


class Attribute(object):
    """ThreatConnect Batch Attribute Object"""

    def __init__(self, tcex, attr_type, attr_value, displayed=False, source=None, formatter=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            tcex: Instance of TcEx
            attr_type: The attribute type.
            attr_value: The attribute value.
            displayed: Boolean value indicating display status.
            source: The attribute source.
            formatter: A method to format the attribute value.
        """
        self.tcex = tcex
        self._attribute_data = {
            'displayed': displayed,
            'type': attr_type
        }
        # format the value
        if formatter is not None:
            attr_value = formatter(attr_value)
        self._attribute_data['value'] = attr_value
        # add source if provided
        if source is not None:
            self._attribute_data['source'] = source

    @property
    def data(self):
        """Return Attribute data"""
        return self._attribute_data

    @property
    def displayed(self):
        """Return Attribute displayed"""
        return self._attribute_data.get('displayed')

    @displayed.setter
    def displayed(self, displayed):
        """Set Attribute displayed"""
        self._attribute_data['displayed'] = displayed

    @property
    def source(self):
        """Return Attribute source"""
        return self._attribute_data.get('source')

    @source.setter
    def source(self, source):
        """Set Attribute source"""
        self._attribute_data['source'] = source

    @property
    def type(self):
        """Return attribute value"""
        return self._attribute_data.get('type')

    @property
    def value(self):
        """Return attribute value"""
        return self._attribute_data.get('value')

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class FileAction(object):
    """ThreatConnect Batch FileAction Object"""

    def __init__(self, tcex, parent_xid, relationship):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            tcex: Instance of TcEx
            name: The security label value.
            description: The security label description.
            color: The security label color.
        """
        self.tcex = tcex
        self.xid = str(uuid.uuid4())
        self._action_data = {
            'indicatorXid': self.xid,
            'relationship': relationship,
            'parentIndicatorXid': parent_xid
        }
        self._children = []

    @property
    def data(self):
        """Return File Occurrence data"""
        if self._children:
            for child in self._children:
                self._action_data.setdefault('children', []).append(child.data)
        return self._action_data

    def action(self, relationship):
        """Add a nested File Action"""
        action_obj = FileAction(self.tcex, self.xid, relationship)
        self._children.append(action_obj)

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class FileOccurrence(object):
    """ThreatConnect Batch FileAction Object"""

    def __init__(self, tcex, file_name=None, path=None, date=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            file_name (string): The Occurrence file name.
            path (string): The Occurrence file path.
            date (string): The Occurrence date.
        """
        self.tcex = tcex
        self._occurrence_data = {}
        if file_name is not None:
            self._occurrence_data['fileName'] = file_name
        if path is not None:
            self._occurrence_data['path'] = path
        if date is not None:
            self._occurrence_data['date'] = self.tcex.utils.format_datetime(
                date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def data(self):
        """Return File Occurrence data"""
        return self._occurrence_data

    @property
    def date(self):
        """Return File Occurrence date"""
        return self._occurrence_data.get('date')

    @date.setter
    def date(self, date):
        """Set File Occurrence date"""
        self._occurrence_data['date'] = self.tcex.utils.format_datetime(
            date, date_format='%Y-%m-%dT%H:%M:%SZ')

    @property
    def file_name(self):
        """Return File Occurrence file name"""
        return self._occurrence_data.get('fileName')

    @file_name.setter
    def file_name(self, file_name):
        """Set File Occurrence file name"""
        self._occurrence_data['fileName'] = file_name

    @property
    def path(self):
        """Return File Occurrence path"""
        return self._occurrence_data.get('path')

    @path.setter
    def path(self, path):
        """Set File Occurrence path"""
        self._occurrence_data['path'] = path

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class SecurityLabel(object):
    """ThreatConnect Batch SecurityLabel Object"""

    def __init__(self, tcex, name, description=None, color=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            tcex: Instance of TcEx
            name: The security label value.
            description: The security label description.
            color: The security label color.
        """
        self.tcex = tcex
        self._label_data = {'name': name}
        # add description if provided
        if description is not None:
            self._label_data['description'] = description
        if color is not None:
            self._label_data['color'] = color

    @property
    def color(self):
        """Return Security Label color"""
        return self._label_data.get('color')

    @color.setter
    def color(self, color):
        """Set Security Label color"""
        self._label_data['color'] = color

    @property
    def data(self):
        """Return Security Label data"""
        return self._label_data

    @property
    def description(self):
        """Return Security Label description"""
        return self._label_data.get('description')

    @description.setter
    def description(self, description):
        """Set Security Label description"""
        self._label_data['description'] = description

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class Tag(object):
    """ThreatConnect Batch Tag Object"""

    def __init__(self, tcex, name, formatter=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            tcex: Instance of TcEx
            name: The tag value.
        """
        self.tcex = tcex
        if formatter is not None:
            name = formatter(name)
        self._tag_data = {
            'name': name
        }

    @property
    def data(self):
        """Return Tag data"""
        return self._tag_data

    @property
    def name(self):
        """Return Tag name"""
        return self._tag_data.get('name')

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)
