# -*- coding: utf-8 -*-
"""ThreatConnect Batch Import Module"""
import json
import uuid

# import local modules for dynamic reference
module = __import__(__name__)


def class_factory(name, base_class, class_dict):
    """Internal method for dynamically building Custom Class"""
    def __init__(self, tcex):
        base_class.__init__(self, tcex)
        for k, v in class_dict.items():
            setattr(self, k, v)

    newclass = type(str(name), (base_class,), {"__init__": __init__})
    return newclass


class Batch(object):
    """ThreatConnect Batch Add Module"""

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

        self._files = []
        self._groups = []
        self._groups_raw = []
        self._indicators = []
        self._indicators_raw = []

        # build custom indicator classes
        #self._gen_indicator_class()

    def _gen_indicator_class(self):
        """Generate Custom Indicator Classes"""
        for entry in self.tcex.indicator_type_data.values():
            name = self.tcex.safe_rt(entry.get('name'))
            # temp fix for API issue where boolean are returned as strings
            entry['custom'] = self.tcex.utils.to_bool(entry.get('custom'))

            if not entry['custom']:
                # only process custom indicators
                continue

            # Custom Indicator can have 3 values. Only add the value if it is set.
            value_fields = []
            if entry.get('value1Label'):
                value_fields.append(entry['value1Label'])
            if entry.get('value2Label'):
                value_fields.append(entry['value2Label'])
            if entry.get('value3Label'):
                value_fields.append(entry['value3Label'])

            class_data = {
                '_api_branch': entry['apiBranch'],
            }
            # Call custom indicator class factory
            setattr(module, name, class_factory(name, Indicator, class_data))

    @property
    def action(self):
        """Return batch action"""
        return self._action

    @action.setter
    def action(self, action):
        """Set batch action"""
        self._action = action

    @property
    def attribute_write_type(self):
        """Return batch attribute write type"""
        return self._attribute_write_type

    @attribute_write_type.setter
    def attribute_write_type(self, attribute_write_type):
        """Set batch attribute write type"""
        self._attribute_write_type = attribute_write_type

    @property
    def halt_on_error(self):
        """Return batch halt_on_error"""
        return self._halt_on_error

    @halt_on_error.setter
    def halt_on_error(self, halt_on_error):
        """Set batch halt_on_error"""
        self._halt_on_error = halt_on_error

    @property
    def batch_data(self):
        """Send the batch request to ThreatConnect"""
        # process group objects
        for group in self._groups:
            # TODO: build file_data ???
            if group.data.get('type') in ['Document', 'Report']:
                self._files.append({
                    'content': group.file_content,
                    'type': group.data.get('type'),
                    'xid': group.data.get('xid'),
                })
            self._groups_raw.append(group.data)

        # process indicator objects
        for indicator in self._indicators:
            self._indicators_raw.append(indicator.data)

        # TODO: clear data for next run ???

        return {
            'group': self._groups_raw,
            'indicator': self._indicators_raw
        }

    @property
    def batch_settings(self):
        """Return batch job settings"""
        return {
            'action': self._action,
            'attributeWriteType': self._attribute_write_type,
            'haltOnError': self._halt_on_error,
            'owner': self._owner,
            'version': 'V2'
        }

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
            self._files.append({
                'content': file_content,
                'type': group_data.get('type'),
                'xid': group_data.get('xid')
            })
        self._groups_raw.append(group_data)

    def add_indicator(self, indicator_data):
        """Add an indicator to Batch Job

        {
            "type": "File",
            "rating": 5.00,
            "confidence": 50,
            "summary": "53c3609411c83f363e051d455ade78a7 : 57a49b478310e4313c54c0fee46e4d70a73dd580 : db31cb2a748b7e0046d8c97a32a7eb4efde32a0593e5dbd58e07a3b4ae6bf3d7",
            "associatedGroupXid": [
                "e336e2dd-5dfb-48cd-a33a-f8809e83e904",
            ],
            "attribute": [{
                "type": "Source",
                "displayed": true,
                "value": "Malware Analysis provided by external AMA."
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
        self._indicators_raw.append(indicator_data)

    def asn(self, as_number, rating=None, confidence=None, xid=None):
        """Add ASN data to Batch object"""
        indicator_obj = ASN(self.tcex, as_number, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def address(self, ip, rating=None, confidence=None, xid=None):
        """Add Address data to Batch object"""
        indicator_obj = Address(self.tcex, ip, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def adversary(self, name, xid=None):
        """Add Adversary data to Batch object"""
        group_obj = Adversary(self.tcex, name, xid)
        self._groups.append(group_obj)
        return group_obj

    def campaign(self, name, first_seen=None, xid=None):
        """Add Campaign data to Batch object"""
        group_obj = Campaign(self.tcex, name, first_seen, xid)
        self._groups.append(group_obj)
        return group_obj

    def cidr(self, block, rating=None, confidence=None, xid=None):
        """Add CIDR data to Batch object"""
        indicator_obj = CIDR(self.tcex, block, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def document(self, name, file_name, malware=None, password=None, xid=None):
        """Add Document data to Batch object"""
        group_obj = Document(self.tcex, name, file_name, malware, password, xid)
        self._groups.append(group_obj)
        return group_obj

    def email(self, name, subject, header, body, to_addr=None, from_addr=None, xid=None):
        """Add Email data to Batch object"""
        group_obj = Email(self.tcex, name, subject, header, body, to_addr, from_addr, xid)
        self._groups.append(group_obj)
        return group_obj

    def email_address(self, address, rating=None, confidence=None, xid=None):
        """Add Email Address data to Batch object"""
        indicator_obj = EmailAddress(self.tcex, address, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def event(self, name, event_date=None, status=None, xid=None):
        """Add Event data to Batch object"""
        group_obj = Event(self.tcex, name, event_date, status, xid)
        self._groups.append(group_obj)
        return group_obj

    def file(self, md5=None, sha1=None, sha256=None, rating=None, confidence=None, xid=None):
        """Add File data to Batch object"""
        indicator_obj = File(self.tcex, md5, sha1, sha256, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def group(self, group_type, name, xid=None):
        """Add Group data to Batch object"""
        group_type = group_type.replace(' ', '')
        group_obj = Group(self.tcex, group_type, name, xid)
        self._groups.append(group_obj)
        return group_obj

    def host(self, hostname, rating=None, confidence=None, xid=None):
        """Add Email Address data to Batch object"""
        indicator_obj = Host(self.tcex, hostname, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def incident(self, name, event_date=None, status=None, xid=None):
        """Add Incident data to Batch object"""
        group_obj = Incident(self.tcex, name, event_date, status, xid)
        self._groups.append(group_obj)
        return group_obj

    def indicator(self, indicator_type, summary, rating=None, confidence=None, xid=None):
        """Add Indicator data to Batch object"""
        indicator_type = indicator_type.replace(' ', '')
        indicator_obj = Indicator(self.tcex, indicator_type, summary, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def intrusion_set(self, name, xid=None):
        """Add Intrusion Set data to Batch object"""
        group_obj = IntrusionSet(self.tcex, name, xid)
        self._groups.append(group_obj)
        return group_obj

    def mutex(self, mutex, rating=None, confidence=None, xid=None):
        """Add Mutex data to Batch object"""
        indicator_obj = Mutex(self.tcex, mutex, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def registry_key(self, key_name, value_name, value_type, rating=None, confidence=None,
                     xid=None):
        """Add Registry Key data to Batch object"""
        indicator_obj = RegistryKey(
            self.tcex, key_name, value_name, value_type, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def report(self, name, file_name, publish_date=None, xid=None):
        """Add Report data to Batch object"""
        group_obj = Report(self.tcex, name, file_name, publish_date, xid)
        self._groups.append(group_obj)
        return group_obj

    def signature(self, name, file_name, file_type, file_text, xid=None):
        """Add Signature data to Batch object"""
        group_obj = Signature(self.tcex, name, file_name, file_type, file_text, xid)
        self._groups.append(group_obj)
        return group_obj

    def submit(self):
        """Send the batch request to ThreatConnect"""
        pass

    def threat(self, name, xid=None):
        """Add Threat data to Batch object"""
        group_obj = Threat(self.tcex, name, xid)
        self._groups.append(group_obj)
        return group_obj

    def user_agent(self, text, rating=None, confidence=None, xid=None):
        """Add User Agent data to Batch object"""
        indicator_obj = UserAgent(self.tcex, text, rating, confidence, xid)
        self._indicators.append(indicator_obj)
        return indicator_obj

    def url(self, text, rating=None, confidence=None, xid=None):
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
        batch_data = self.batch_data
        batch_data['files'] = self._files
        return json.dumps(batch_data, indent=4, sort_keys=True)


#
# Groups
#


class Group(object):
    """ThreatConnect Batch Group Object"""

    def __init__(self, tcex, group_type, name, xid):
        """Initialize Class Properties"""
        self.tcex = tcex
        self._group_data = {
            'name': name,
            'type': group_type,
            'xid': self._xid(xid)
        }
        self._attributes = []
        self._labels = []
        self._tags = []

    @staticmethod
    def _xid(xid):
        """Return a valid xid"""
        if xid is None:
            xid = str(uuid.uuid4())
        return xid

    def add_key_value(self, key, value):
        """Add custom field to Group object"""
        self._group_data[key] = value

    def association(self, group_xid):
        """Add association using xid value"""
        self._group_data.setdefault('associatedGroupXid', []).append(group_xid)

    def attribute(self, attr_type, attr_value, displayed=None, source=None, conversion_method=None):
        """Return instance of Attribute"""
        attr = Attribute(self.tcex, attr_type, attr_value, displayed, source, conversion_method)
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

    def tag(self, name):
        """Return instance of Tag"""
        tag = Tag(self.tcex, name)
        self._tags.append(tag)
        return tag

    @property
    def xid(self):
        """Return Group xid"""
        return self._group_data.get('xid')

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self._group_data, indent=4)


class Adversary(Group):
    """ThreatConnect Batch Adversary Object"""

    def __init__(self, tcex, name, xid):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
        """
        super(Adversary, self).__init__(tcex, 'Adversary', name, xid)
        tcex.log.debug('Adversary Object')


class Campaign(Group):
    """ThreatConnect Batch Campaign Object"""

    def __init__(self, tcex, name, first_seen=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            first_seen (string): The date of the campaign was first seen
                                 (date will be auto-formatted).
        """
        super(Campaign, self).__init__(tcex, 'Campaign', name, xid)
        tcex.log.debug('Campaign Object')
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

    def __init__(self, tcex, name, file_name, malware=False, password=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            file_name (string): The name of the attached document.
            malware (boolean): Indicates the attached document is malware.
        """
        super(Document, self).__init__(tcex, 'Document', name, xid)
        tcex.log.debug('Document Object')
        self._group_data['fileName'] = file_name
        if malware:
            self._group_data['malware'] = malware
        if password is not None:
            self._group_data['password'] = password
        self._file_content = None

    @property
    def file_content(self):
        """Return Document file data"""
        return self._file_content

    @file_content.setter
    def file_content(self, file_content):
        """Set Document file data"""
        self._file_content = file_content

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

    def __init__(self, tcex, name, subject, header, body, to_addr=None, from_addr=None, xid=None):
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
        tcex.log.debug('Email Object')
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

    def __init__(self, tcex, name, event_date=None, status=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            event_date (string): The date of the Event (date will be auto-formatted).
        """
        super(Event, self).__init__(tcex, 'Event', name, xid)
        tcex.log.debug('Event Object')
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

    def __init__(self, tcex, name, event_date=None, status=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            event_date (string): The date of the event (date will be auto-formatted).
            status (string): The status of the Incident.
        """
        super(Incident, self).__init__(tcex, 'Incident', name, xid)
        tcex.log.debug('Incident Object')
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

    def __init__(self, tcex, name, xid):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
        """
        super(IntrusionSet, self).__init__(tcex, 'Intrusion Set', name, xid)
        tcex.log.debug('IntrustionSet Object')


class Report(Group):
    """ThreatConnect Batch Report Object"""

    def __init__(self, tcex, name, file_name, publish_date=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            file_name (string): The name of the attached document.
            publish_date (string): The date the report was published (date will be auto-formatted).
        """
        super(Report, self).__init__(tcex, 'Report', name, xid)
        tcex.log.debug('Report Object')
        self._group_data['fileName'] = file_name
        if publish_date is not None:
            self._group_data['publishDate'] = self.tcex.utils.format_datetime(
                publish_date, date_format='%Y-%m-%dT%H:%M:%SZ')
        self._file_content = None

    @property
    def file_content(self):
        """Return Document file data"""
        return self._file_content

    @file_content.setter
    def file_content(self, file_content):
        """Set Document file data"""
        self._file_content = file_content

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

    def __init__(self, tcex, name, file_name, file_type, file_text, xid=None):
        """Initialize Class Properties

        Valid file_types:
        + Snort ®
        + Suricata
        + YARA
        + ClamAV ®
        + OpenIOC
        + CybOX™
        + Bro
        + Regex
        + Splunk ® Search Processing Language (SPL)

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            file_name (string): The Signature file name.
            file_type (string): The Signature file type.
            file_text (string): The Signature text.
        """
        super(Signature, self).__init__(tcex, 'Signature', name, xid)
        tcex.log.debug('Signature Object')
        self._group_data['fileName'] = file_name
        self._group_data['fileType'] = file_type
        self._group_data['fileText'] = file_text


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
        tcex.log.debug('Threat Object')


#
# Indicators
#


class Indicator(object):
    """ThreatConnect Batch Indicator Object"""

    def __init__(self, tcex, indicator_type, summary, rating=None, confidence=None, xid=None):
        """Initialize Class Properties"""
        self.tcex = tcex
        self._indicator_data = {
            'summary': summary,
            'type': indicator_type,
            'xid': self._xid(xid)
        }
        if confidence is not None:
            self._indicator_data['confidence'] = confidence
        if rating is not None:
            self._indicator_data['rating'] = rating
        self._attributes = []
        self._labels = []
        self._tags = []

    @staticmethod
    def _xid(xid):
        """Return a valid xid"""
        if xid is None:
            xid = str(uuid.uuid4())
        return xid

    def add_key_value(self, key, value):
        """Add custom field to Indicator object"""

        if self._indicator_data.get('type') == 'Host':
            if key == 'dnsActive':
                key = 'flag1'
            elif key == 'whoisActive':
                key = 'flag2'
        self._indicator_data[key] = value

    @staticmethod
    def build_summary(val1, val2, val3):
        """Build the Indicator summary using available values"""
        summary = []
        if val1 is not None:
            summary.append(val1)
        if val2 is not None:
            summary.append(val2)
        if val3 is not None:
            summary.append(val3)
        if not summary:
            raise RuntimeError('No hash values provided.')
        return ' : '.join(summary)

    def association(self, group_xid):
        """Add association using xid value"""
        self._indicator_data.setdefault('associatedGroupXid', []).append(group_xid)

    def attribute(self, attr_type, attr_value, displayed=None, source=None, conversion_method=None):
        """Return instance of Attribute"""
        attr = Attribute(self.tcex, attr_type, attr_value, displayed, source, conversion_method)
        self._attributes.append(attr)
        return attr

    @property
    def confidence(self):
        """Return Indicator confidence"""
        return self._indicator_data.get('confidence')

    @confidence.setter
    def confidence(self, confidence):
        """Set Indicator confidence"""
        self._indicator_data['confidence'] = confidence

    @property
    def data(self):
        """Return Indicator data"""
        # add attributes
        if self._attributes:
            self._indicator_data['attribute'] = []
            for attr in self._attributes:
                self._indicator_data['attribute'].append(attr.data)
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
    def rating(self):
        """Return Indicator rating"""
        return self._indicator_data.get('rating')

    @rating.setter
    def rating(self, rating):
        """Set Indicator rating"""
        self._indicator_data['rating'] = rating

    @property
    def summary(self):
        """Return Indicator summary"""
        return self._indicator_data.get('summary')

    def security_label(self, name, description=None, color=None):
        """Return instance of Tag"""
        label = SecurityLabel(self.tcex, name, description, color)
        self._labels.append(label)
        return label

    def tag(self, name):
        """Return instance of Tag"""
        tag = Tag(self.tcex, name)
        self._tags.append(tag)
        return tag

    @property
    def xid(self):
        """Return Group xid"""
        return self._indicator_data.get('xid')

    def __str__(self):
        """Return string represtentation of object"""
        return json.dumps(self._indicator_data, indent=4)


class Address(Indicator):
    """ThreatConnect Batch Address Object"""

    def __init__(self, tcex, ip, rating=None, confidence=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            ip (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(Address, self).__init__(tcex, 'Address', ip, rating, confidence, xid)
        tcex.log.debug('Address Object')


class ASN(Indicator):
    """ThreatConnect Batch ASN Object"""

    def __init__(self, tcex, as_number, rating=None, confidence=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            as_number (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(ASN, self).__init__(tcex, 'ASN', as_number, rating, confidence, xid)
        tcex.log.debug('ASN Object')


class CIDR(Indicator):
    """ThreatConnect Batch CIDR Object"""

    def __init__(self, tcex, block, rating=None, confidence=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            block (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(CIDR, self).__init__(tcex, 'CIDR', block, rating, confidence, xid)
        tcex.log.debug('CIDR Object')


class EmailAddress(Indicator):
    """ThreatConnect Batch EmailAddress Object"""

    def __init__(self, tcex, address, rating=None, confidence=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            address (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(EmailAddress, self).__init__(tcex, 'EmailAddress', address, rating, confidence, xid)
        tcex.log.debug('Email Address Object')


class File(Indicator):
    """ThreatConnect Batch File Object"""

    def __init__(self, tcex, md5=None, sha1=None, sha256=None, size=None, rating=None,
                 confidence=None, xid=None):
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
        summary = self.build_summary(md5, sha1, sha256)  # build the indicator summary
        super(File, self).__init__(tcex, 'File', summary, rating, confidence, xid)
        tcex.log.debug('File Object')
        self._indicator_data['type'] = 'File'
        if size is not None:
            self._indicator_data['size'] = size

    @property
    def md5(self):
        """Return Indicator md5"""
        return self._indicator_data.get('md5')

    @md5.setter
    def md5(self, md5):
        """Set Indicator md5"""
        self._indicator_data['md5'] = md5

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
        return self._indicator_data.get('size')

    @size.setter
    def size(self, size):
        """Set Indicator size"""
        self._indicator_data['size'] = size


class Host(Indicator):
    """ThreatConnect Batch Host Object"""

    def __init__(self, tcex, hostname, dns_active=False, whois_active=False, rating=None,
                 confidence=None, xid=None):
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
        tcex.log.debug('Host Object')
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

    def __init__(self, tcex, mutex, rating=None, confidence=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            mutex (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(Mutex, self).__init__(tcex, 'Mutex', mutex, rating, confidence, xid)
        tcex.log.debug('Mutex Object')


class RegistryKey(Indicator):
    """ThreatConnect Batch Registry Key Object"""

    def __init__(self, tcex, key_name, value_name, value_type, rating=None, confidence=None,
                 xid=None):
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
        tcex.log.debug('Mutex Object')


class URL(Indicator):
    """ThreatConnect Batch URL Object"""

    def __init__(self, tcex, text, rating=None, confidence=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            text (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(URL, self).__init__(tcex, 'URL', text, rating, confidence, xid)
        tcex.log.debug('URL Object')


class UserAgent(Indicator):
    """ThreatConnect Batch User Agent Object"""

    def __init__(self, tcex, text, rating=None, confidence=None, xid=None):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            text (string): The Indicator value.
            rating (string): The Indicator threat rating.
            confidence (string): The Indicator threat confidence.
            xid (string): The Group external id.
        """
        super(UserAgent, self).__init__(tcex, 'User Agent', text, rating, confidence, xid)
        tcex.log.debug('User Agent Object')


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
        tcex.log.debug('Attribute Object')
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
        tcex.log.debug('Security Label Object')
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


class Tag(object):
    """ThreatConnect Batch Tag Object"""

    def __init__(self, tcex, name):
        """Initialize Class Properties

        Args:
            tcex (TcEx Instance): Instance of TcEx
            xid (string): The Group external id.
            name (string): The Group name.
            tcex: Instance of TcEx
            name: The tag value.
        """
        tcex.log.debug('Tag Object')
        self.tcex = tcex
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
