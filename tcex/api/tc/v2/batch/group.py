"""TcEx Framework Module"""

# standard library
import json
import uuid
from collections.abc import Callable
from typing import Any

# first-party
from tcex.api.tc.v2.batch.attribute import Attribute
from tcex.api.tc.v2.batch.security_label import SecurityLabel
from tcex.api.tc.v2.batch.tag import Tag
from tcex.util import Util


class Group:
    """ThreatConnect Batch Group Object"""

    __slots__ = [
        '_attributes',
        '_file_content',
        '_group_data',
        '_labels',
        '_name',
        '_processed',
        '_type',
        '_tags',
        'file_content',
        'malware',
        'password',
        'status',
        'util',
    ]

    def __init__(self, group_type: str, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            group_type (str): The ThreatConnect define Group type.
            name (str): The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            xid (str, kwargs): The external id for this Group.
        """
        self._name = name
        self._group_data: dict[str, bool | int | list | str] = {'name': name, 'type': group_type}
        self._type = group_type

        # properties
        self._attributes = []
        self._labels = []
        self._file_content = None
        self._tags = []
        self._processed = False
        self.util = Util()

        # process all kwargs and update metadata field names
        for arg, value in kwargs.items():
            self.add_key_value(arg, value)
        # set xid to random and unique uuid4 value if not provided
        if kwargs.get('xid') is None:
            self._group_data['xid'] = str(uuid.uuid4())

    @property
    def _metadata_map(self) -> dict:
        """Return metadata map for Group objects."""
        return {
            'date_added': 'dateAdded',
            'event_date': 'eventDate',
            'file_name': 'fileName',
            'file_text': 'fileText',
            'file_type': 'fileType',
            'first_seen': 'firstSeen',
            'last_seen': 'lastSeen',
            'external_date_created': 'externalDateCreated',
            'external_date_expires': 'externalDateExpires',
            'external_last_modified': 'externalLastModified',
            'from_addr': 'from',
            'publish_date': 'publishDate',
            'to_addr': 'to',
        }

    def add_file(self, filename: str, file_content: bytes | Callable[[str], Any] | str):
        """Add a file for Document and Report types.

        Example::

            document = tcex.batch.group('Document', 'My Document')
            document.add_file('my_file.txt', 'my contents')

        Args:
            filename: The name of the file.
            file_content: The contents of the file or callback to get contents.
        """
        self._group_data['fileName'] = filename
        self._file_content = file_content

    def add_key_value(self, key: str, value: str):
        """Add custom field to Group object.

        .. note:: The key must be the exact name required by the batch schema.

        Example::

            document = tcex.batch.group('Document', 'My Document')
            document.add_key_value('fileName', 'something.pdf')

        Args:
            key: The field key to add to the JSON batch data.
            value: The field value to add to the JSON batch data.
        """
        key = self._metadata_map.get(key, key)
        if key in {
            'dateAdded',
            'eventDate',
            'firstSeen',
            'lastSeen',
            'externalDateCreated',
            'externalDateExpires',
            'externalLastModified',
            'publishDate',
        }:
            if value is not None:
                self._group_data[key] = self.util.any_to_datetime(value).strftime(
                    '%Y-%m-%dT%H:%M:%SZ'
                )
        elif key == 'file_content':
            # file content arg is not part of Group JSON
            pass
        else:
            self._group_data[key] = value

    def association(self, group_xid: str):
        """Add association using xid value.

        Args:
            group_xid: The external id of the Group to associate.
        """
        self._group_data.setdefault('associatedGroupXid', []).append(group_xid)  # type: ignore

    def attribute(
        self,
        attr_type: str,
        attr_value: str,
        displayed: bool = False,
        source: str | None = None,
        unique: bool = True,
        formatter: Callable[[str], str] | None = None,
    ) -> Attribute:
        """Return instance of Attribute

        unique:
            * False - Attribute type:value can be duplicated.
            * 'Type' - Attribute type has to be unique (e.g., only 1 Description Attribute).
            * True - Attribute type:value combo must be unique.

        Args:
            attr_type: The ThreatConnect defined attribute type.
            attr_value: The value for this attribute.
            displayed: If True the supported attribute will be marked for display.
            source: The source value for this attribute.
            unique: Control attribute creation.
            formatter: A callable that takes a single attribute
                value and returns a single formatted value.

        Returns:
            Attribute: An instance of the Attribute class.
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
    def data(self) -> dict:
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
    def date_added(self) -> str | None:
        """Return Group dateAdded."""
        return self._group_data.get('dateAdded')  # type: ignore

    @date_added.setter
    def date_added(self, date_added: str):
        """Set Indicator dateAdded."""
        self._group_data['dateAdded'] = self.util.any_to_datetime(date_added).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def first_seen(self) -> str:
        """Return Indicator firstSeen."""
        return self._group_data.get('firstSeen')  # type: ignore

    @first_seen.setter
    def first_seen(self, first_seen: str):
        """Set Indicator firstSeen."""
        self._group_data['firstSeen'] = self.util.any_to_datetime(first_seen).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def last_seen(self) -> str:
        """Return Indicator lastSeen."""
        return self._group_data.get('lastSeen')  # type: ignore

    @last_seen.setter
    def last_seen(self, last_seen: str):
        """Set Indicator lastSeen."""
        self._group_data['lastSeen'] = self.util.any_to_datetime(last_seen).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def external_date_created(self) -> str:
        """Return Indicator externalDateCreated."""
        return self._group_data.get('externalDateCreated')  # type: ignore

    @external_date_created.setter
    def external_date_created(self, external_date_created: str):
        """Set Indicator externalDateCreated."""
        external_date_created = self.util.any_to_datetime(external_date_created).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )
        self._group_data['externalDateCreated'] = external_date_created

    @property
    def external_date_expires(self) -> str:
        """Return Indicator externalDateExpires."""
        return self._group_data.get('externalDateExpires')  # type: ignore

    @external_date_expires.setter
    def external_date_expires(self, external_date_expires: str):
        """Set Indicator externalDateExpires."""
        external_date_expires = self.util.any_to_datetime(external_date_expires).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )
        self._group_data['externalDateExpires'] = external_date_expires

    @property
    def external_last_modified(self) -> str:
        """Return Indicator externalLastModified."""
        return self._group_data.get('externalLastModified')  # type: ignore

    @external_last_modified.setter
    def external_last_modified(self, external_date_last_modified: str):
        """Set Indicator externalLastModified."""
        external_date_last_modified = self.util.any_to_datetime(
            external_date_last_modified
        ).strftime('%Y-%m-%dT%H:%M:%SZ')
        self._group_data['externalLastModified'] = external_date_last_modified

    @property
    def file_data(self) -> dict:
        """Return Group file (only supported for Document and Report)."""
        return {
            'fileContent': self._file_content,
            'fileName': self._group_data.get('fileName'),
            'type': self._group_data.get('type'),
        }

    @property
    def name(self) -> str:
        """Return Group name."""
        return self._group_data.get('name')  # type: ignore

    @property
    def processed(self) -> bool:
        """Return processed value.

        .. note:: Processed value indicates that a group with this xid has already been processed.
        """
        return self._processed

    @processed.setter
    def processed(self, processed: bool):
        """Set processed."""
        self._processed = processed

    def security_label(
        self, name: str, description: str | None = None, color: str | None = None
    ) -> SecurityLabel:
        """Return instance of SecurityLabel.

        .. note:: The provided security label will be create if it doesn't exist. If the security
            label already exists nothing will be changed.

        Args:
            name: The value for this security label.
            description: A description for this security label.
            color: A color (hex value) for this security label.

        Returns:
            SecurityLabel: An instance of the SecurityLabel class.
        """
        label = SecurityLabel(name, description, color)
        for label_data in self._labels:
            if label_data.name == name:
                label = label_data
                break
        else:
            self._labels.append(label)
        return label

    def tag(self, name: str, formatter: Callable[[str], str] | None = None) -> Tag:
        """Return instance of Tag.

        Args:
            name: The value for this tag.
            formatter: A callable that take a tag value and returns a formatted tag.

        Returns:
            Tag: An instance of the Tag class.
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
    def type(self) -> str:
        """Return Group type."""
        return self._group_data.get('type')  # type: ignore

    @property
    def xid(self) -> str:
        """Return Group xid."""
        return self._group_data.get('xid')  # type: ignore

    def __str__(self) -> str:
        """Return string representation of object."""
        return json.dumps(self.data, indent=4)


class Adversary(Group):
    """ThreatConnect Batch Adversary Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Adversary', name, **kwargs)


class AttackPattern(Group):
    """ThreatConnect Batch Attack Pattern Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Attack Pattern', name, **kwargs)


class Campaign(Group):
    """ThreatConnect Batch Campaign Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            first_seen (str, kwargs): The first seen datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Campaign', name, **kwargs)


class CourseOfAction(Group):
    """ThreatConnect Batch Course Of Action Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Course of Action', name, **kwargs)


class Document(Group):
    """ThreatConnect Batch Document Object"""

    __slots__ = ['_file_data']

    def __init__(self, name: str, file_name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            file_name: The name for the attached file for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                file content.
            malware (bool, kwargs): If true the file is considered malware.
            password (bool, kwargs): If malware is true a password for the zip archive is required.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Document', name, **kwargs)
        self._group_data['fileName'] = file_name
        # file data/content to upload
        self._file_content = kwargs.get('file_content')

    @property
    def file_data(self) -> dict:
        """Return Group files."""
        return {
            'fileContent': self._file_content,
            'fileName': self._group_data.get('fileName'),
            'type': self._group_data.get('type'),
        }

    @property
    def malware(self) -> bool:
        """Return Document malware."""
        return self._group_data.get('malware', False)  # type: ignore

    @malware.setter
    def malware(self, malware: bool):
        """Set Document malware."""
        self._group_data['malware'] = malware  # type: ignore

    @property
    def password(self) -> str:
        """Return Document password."""
        return self._group_data.get('password', False)  # type: ignore

    @password.setter
    def password(self, password: str):
        """Set Document password."""
        self._group_data['password'] = password


class Email(Group):
    """ThreatConnect Batch Email Object"""

    __slots__ = []

    def __init__(self, name: str, subject: str, header: str, body: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            subject: The subject for this Email.
            header: The header for this Email.
            body: The body for this Email.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            from_addr (str, kwargs): The **from** address for this Email.
            to_addr (str, kwargs): The **to** address for this Email.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Email', name, **kwargs)
        self._group_data['subject'] = subject
        self._group_data['header'] = header
        self._group_data['body'] = body
        self._group_data['score'] = 0

    @property
    def from_addr(self) -> str:
        """Return Email to."""
        return self._group_data.get('to')  # type: ignore

    @from_addr.setter
    def from_addr(self, from_addr: str):
        """Set Email from."""
        self._group_data['from'] = from_addr

    @property
    def score(self) -> str:
        """Return Email to."""
        return self._group_data.get('score')  # type: ignore

    @score.setter
    def score(self, score: str):
        """Set Email from."""
        self._group_data['score'] = score

    @property
    def to_addr(self) -> str:
        """Return Email to."""
        return self._group_data.get('to')  # type: ignore

    @to_addr.setter
    def to_addr(self, to_addr: str):
        """Set Email to."""
        self._group_data['to'] = to_addr


class Event(Group):
    """ThreatConnect Batch Event Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Valid Values:
        + Escalated
        + False Positive
        + Needs Review
        + No Further Action

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Event', name, **kwargs)

    @property
    def event_date(self) -> str:
        """Return the Events "event date" value."""
        return self._group_data.get('firstSeen')  # type: ignore

    @event_date.setter
    def event_date(self, event_date: str):
        """Set the Events "event date" value."""
        self._group_data['eventDate'] = self.util.any_to_datetime(event_date).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def status(self) -> str:
        """Return the Events status value."""
        return self._group_data.get('status')  # type: ignore

    @status.setter
    def status(self, status: str):
        """Set the Events status value."""
        self._group_data['status'] = status


class Incident(Group):
    """ThreatConnect Batch Incident Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

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
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            event_date (str, kwargs): The event datetime expression for this Group.
            status (str, kwargs): The status for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Incident', name, **kwargs)

    @property
    def event_date(self) -> str:
        """Return Incident event date."""
        return self._group_data.get('eventDate')  # type: ignore

    @event_date.setter
    def event_date(self, event_date: str):
        """Set Incident event_date."""
        self._group_data['eventDate'] = self.util.any_to_datetime(event_date).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def status(self) -> str:
        """Return Incident status."""
        return self._group_data.get('status')  # type: ignore

    @status.setter
    def status(self, status: str):
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
    """ThreatConnect Batch Intrusion Set Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Intrusion Set', name, **kwargs)


class Malware(Group):
    """ThreatConnect Batch Malware Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Malware', name, **kwargs)


class Report(Group):
    """ThreatConnect Batch Report Object"""

    __slots__ = []

    def __init__(self, name, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            file_name (str, kwargs): The name for the attached file for this Group.
            file_content (str;method, kwargs): The file contents or callback method to retrieve
                file content.
            publish_date (str, kwargs): The publish datetime expression for this Group.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Report', name, **kwargs)
        # file data/content to upload
        self._file_content = kwargs.get('file_content')

    @property
    def file_data(self) -> dict:
        """Return Group files."""
        return {
            'fileContent': self._file_content,
            'fileName': self._group_data.get('fileName'),
            'type': self._group_data.get('type'),
        }

    @property
    def publish_date(self) -> str:
        """Return Report publish date."""
        return self._group_data.get('publishDate')  # type: ignore

    @publish_date.setter
    def publish_date(self, publish_date: str):
        """Set Report publish date"""
        self._group_data['publishDate'] = self.util.any_to_datetime(publish_date).strftime(
            '%Y-%m-%dT%H:%M:%SZ'
        )


class Signature(Group):
    """ThreatConnect Batch Signature Object"""

    __slots__ = []

    def __init__(self, name: str, file_name: str, file_type: str, file_text: str, **kwargs):
        """Initialize instance properties.

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
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Signature', name, **kwargs)
        self._group_data['fileName'] = file_name
        self._group_data['fileType'] = file_type
        self._group_data['fileText'] = file_text


class Tactic(Group):
    """ThreatConnect Batch Tactic Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Tactic', name, **kwargs)


class Threat(Group):
    """ThreatConnect Batch Threat Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Threat', name, **kwargs)


class Tool(Group):
    """ThreatConnect Batch Tool Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Tool', name, **kwargs)


class Vulnerability(Group):
    """ThreatConnect Batch Vulnerability Object"""

    __slots__ = []

    def __init__(self, name: str, **kwargs):
        """Initialize instance properties.

        Args:
            name: The name for this Group.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            date_added (str, kwargs): The date timestamp the Indicator was created.
            xid (str, kwargs): The external id for this Group.
        """
        super().__init__('Vulnerability', name, **kwargs)
