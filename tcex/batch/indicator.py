"""ThreatConnect Batch Import Module"""
# standard library
import json
import uuid
from typing import Callable, Optional

from ..utils import Utils
from .attribute import Attribute
from .security_label import SecurityLabel
from .tag import Tag

# import local modules for dynamic reference
module = __import__(__name__)


def custom_indicator_class_factory(indicator_type, base_class, class_dict, value_fields):
    """Return internal methods for dynamically building Custom Indicator Class."""
    value_count = len(value_fields)

    def init_1(self, tcex, value1, xid, **kwargs):  # pylint: disable=possibly-unused-variable
        """Init method for Custom Indicator Types with one value"""
        summary = self.build_summary(value1)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, xid, **kwargs)
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_2(
        self, tcex, value1, value2, xid, **kwargs
    ):  # pylint: disable=possibly-unused-variable
        """Init method for Custom Indicator Types with two values."""
        summary = self.build_summary(value1, value2)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, xid, **kwargs)
        for k, v in class_dict.items():
            setattr(self, k, v)

    def init_3(
        self, tcex, value1, value2, value3, xid, **kwargs
    ):  # pylint: disable=possibly-unused-variable
        """Init method for Custom Indicator Types with three values."""
        summary = self.build_summary(value1, value2, value3)  # build the indicator summary
        base_class.__init__(self, tcex, indicator_type, summary, xid, **kwargs)
        for k, v in class_dict.items():
            setattr(self, k, v)

    class_name = indicator_type.replace(' ', '')
    init_method = locals()[f'init_{value_count}']
    newclass = type(str(class_name), (base_class,), {'__init__': init_method})
    return newclass


class Indicator:
    """ThreatConnect Batch Indicator Object"""

    __slots__ = [
        '_attributes',
        '_file_actions',
        '_indicator_data',
        '_labels',
        '_occurrences',
        '_summary',
        '_tags',
        '_type',
        '_utils',
    ]

    def __init__(self, indicator_type: str, summary: str, **kwargs):
        """Initialize Class Properties.

        Args:
            indicator_type: The ThreatConnect define Indicator type.
            summary: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        self._utils = Utils()
        self._summary = summary
        self._type = indicator_type
        self._indicator_data = {'summary': summary, 'type': indicator_type}
        # process all kwargs and update metadata field names
        for arg, value in kwargs.items():
            self.add_key_value(arg, value)
        # set xid to random and unique uuid4 value if not provided
        if kwargs.get('xid') is None:
            self._indicator_data['xid'] = str(uuid.uuid4())
        self._attributes = []
        self._file_actions = []
        self._labels = []
        self._occurrences = []
        self._tags = []

    @property
    def _metadata_map(self) -> dict:
        """Return metadata map for Indicator objects."""
        return {
            'date_added': 'dateAdded',
            'dnsActive': 'flag1',
            'dns_active': 'flag1',
            'last_modified': 'lastModified',
            'private_flag': 'privateFlag',
            'size': 'intValue1',
            'whoisActive': 'flag2',
            'whois_active': 'flag2',
        }

    def add_key_value(self, key: str, value: str) -> None:
        """Add custom field to Indicator object.

        .. note:: The key must be the exact name required by the batch schema.

        Example::

            file_hash = tcex.batch.file('File', '1d878cdc391461e392678ba3fc9f6f32')
            file_hash.add_key_value('size', '1024')

        Args:
            key: The field key to add to the JSON batch data.
            value: The field value to add to the JSON batch data.
        """
        key = self._metadata_map.get(key, key)
        if key in ['dateAdded', 'lastModified']:
            self._indicator_data[key] = self._utils.datetime.format_datetime(
                value, date_format='%Y-%m-%dT%H:%M:%SZ'
            )
        elif key == 'confidence':
            self._indicator_data[key] = int(value)
        elif key == 'rating':
            self._indicator_data[key] = float(value)
        else:
            self._indicator_data[key] = value

    @property
    def active(self) -> bool:
        """Return Indicator active."""
        return self._indicator_data.get('active')

    @active.setter
    def active(self, active: bool):
        """Set Indicator active."""
        self._indicator_data['active'] = self._utils.to_bool(active)

    def association(self, group_xid: str) -> None:
        """Add association using xid value.

        Args:
            group_xid (str): The external id of the Group to associate.
        """
        association = {'groupXid': group_xid}
        self._indicator_data.setdefault('associatedGroups', []).append(association)

    def attribute(
        self,
        attr_type: str,
        attr_value: str,
        displayed: Optional[bool] = False,
        source: Optional[str] = None,
        unique: Optional[bool] = True,
        formatter: Optional[Callable[[str], str]] = None,
    ) -> Attribute:
        """Return instance of Attribute

        unique:
            * False - Attribute type:value can be duplicated.
            * Type - Attribute type has to be unique (e.g., only 1 Description Attribute).
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

    @staticmethod
    def build_summary(
        val1: Optional[str] = None, val2: Optional[str] = None, val3: Optional[str] = None
    ) -> str:
        """Build the Indicator summary using available values."""
        summary = []
        if val1 is not None:
            summary.append(val1)
        if val2 is not None:
            summary.append(val2)
        if val3 is not None:
            summary.append(val3)
        if not summary:
            # Indicator object has no logger to output warning
            pass
        return ' : '.join(summary)

    @property
    def confidence(self) -> int:
        """Return Indicator confidence."""
        return self._indicator_data.get('confidence')

    @confidence.setter
    def confidence(self, confidence: int):
        """Set Indicator confidence."""
        self._indicator_data['confidence'] = int(confidence)

    @property
    def data(self) -> dict:
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

    @property
    def date_added(self) -> str:
        """Return Indicator dateAdded."""
        return self._indicator_data.get('dateAdded')

    @date_added.setter
    def date_added(self, date_added: str):
        """Set Indicator dateAdded."""
        self._indicator_data['dateAdded'] = self._utils.datetime.format_datetime(
            date_added, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def last_modified(self) -> str:
        """Return Indicator lastModified."""
        return self._indicator_data.get('lastModified')

    @last_modified.setter
    def last_modified(self, last_modified: str):
        """Set Indicator lastModified."""
        self._indicator_data['lastModified'] = self._utils.datetime.format_datetime(
            last_modified, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

    def occurrence(
        self,
        file_name: Optional[str] = None,
        path: Optional[str] = None,
        date: Optional[str] = None,
    ) -> object:
        """Add a file Occurrence.

        Args:
            file_name (str, optional): The file name for this occurrence.
            path (str, optional): The file path for this occurrence.
            date (str, optional): The datetime expression for this occurrence.

        Returns:
            FileOccurrence: An instance of Occurrence.
        """
        if self._indicator_data.get('type') != 'File':
            # Indicator object has no logger to output warning
            return None

        occurrence_obj = FileOccurrence(file_name, path, date)
        self._occurrences.append(occurrence_obj)
        return occurrence_obj

    @property
    def private_flag(self) -> bool:
        """Return Indicator private flag."""
        return self._indicator_data.get('privateFlag')

    @private_flag.setter
    def private_flag(self, private_flag: bool):
        """Set Indicator private flag."""
        self._indicator_data['privateFlag'] = self._utils.to_bool(private_flag)

    @property
    def rating(self) -> float:
        """Return Indicator rating."""
        return self._indicator_data.get('rating')

    @rating.setter
    def rating(self, rating: float):
        """Set Indicator rating."""
        self._indicator_data['rating'] = float(rating)

    @property
    def summary(self) -> str:
        """Return Indicator summary."""
        return self._indicator_data.get('summary')

    def security_label(
        self, name: str, description: Optional[str] = None, color: Optional[str] = None
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

    def tag(self, name: str, formatter: Optional[Callable[[str], str]] = None) -> Tag:
        """Return instance of Tag.

        Args:
            name: The value for this tag.
            formatter: A method that take a tag value and returns a formatted tag.

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
        return self._indicator_data.get('type')

    @property
    def xid(self) -> str:
        """Return Group xid."""
        return self._indicator_data.get('xid')

    def __str__(self) -> str:
        """Return string represtentation of object"""
        return json.dumps(self.data, indent=4)


class Address(Indicator):
    """ThreatConnect Batch Address Object"""

    __slots__ = []

    def __init__(self, ip: str, **kwargs):
        """Initialize Class Properties.

        Args:
            ip: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('Address', ip, **kwargs)


class ASN(Indicator):
    """ThreatConnect Batch ASN Object."""

    __slots__ = []

    def __init__(self, as_number: str, **kwargs):
        """Initialize Class Properties.

        Args:
            as_number: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('ASN', as_number, **kwargs)


class CIDR(Indicator):
    """ThreatConnect Batch CIDR Object"""

    __slots__ = []

    def __init__(self, block: str, **kwargs):
        """Initialize Class Properties.

        Args:
            block: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('CIDR', block, **kwargs)


class EmailAddress(Indicator):
    """ThreatConnect Batch EmailAddress Object"""

    __slots__ = []

    def __init__(self, address: str, **kwargs):
        """Initialize Class Properties.

        Args:
            address: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('EmailAddress', address, **kwargs)


class File(Indicator):
    """ThreatConnect Batch File Object"""

    __slots__ = []

    def __init__(
        self,
        md5: Optional[str] = None,
        sha1: Optional[str] = None,
        sha256: Optional[str] = None,
        **kwargs,
    ):
        """Initialize Class Properties.

        Args:
            md5: The md5 value for this Indicator.
            sha1: The sha1 value for this Indicator.
            sha256: The sha256 value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            size (str, kwargs): The file size for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        summary = self.build_summary(md5, sha1, sha256)  # build the indicator summary
        super().__init__('File', summary, **kwargs)
        # self._file_action = []

    def action(self, relationship: str) -> object:
        """Add a File Action."""
        action_obj = FileAction(self._indicator_data.get('xid'), relationship)
        self._file_actions.append(action_obj)
        return action_obj

    @property
    def md5(self) -> str:
        """Return Indicator md5."""
        return self._indicator_data.get('md5')

    @md5.setter
    def md5(self, md5: str):
        """Set Indicator md5."""
        self._indicator_data['md5'] = md5

    @property
    def sha1(self) -> str:
        """Return Indicator sha1."""
        return self._indicator_data.get('sha1')

    @sha1.setter
    def sha1(self, sha1: str):
        """Set Indicator sha1."""
        self._indicator_data['sha1'] = sha1

    @property
    def sha256(self) -> str:
        """Return Indicator sha256."""
        return self._indicator_data.get('sha256')

    @sha256.setter
    def sha256(self, sha256: str):
        """Set Indicator sha256."""
        self._indicator_data['sha256'] = sha256

    @property
    def size(self) -> int:
        """Return Indicator size."""
        return self._indicator_data.get('intValue1')

    @size.setter
    def size(self, size: int):
        """Set Indicator size."""
        self._indicator_data['intValue1'] = size


class Host(Indicator):
    """ThreatConnect Batch Host Object"""

    __slots__ = []

    def __init__(self, hostname: str, **kwargs):
        """Initialize Class Properties.

        Args:
            hostname: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            dns_active (bool, kwargs): If True DNS active is enabled for this indicator.
            whois_active (bool, kwargs): If True WhoIs active is enabled for this indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('Host', hostname, **kwargs)

    @property
    def dns_active(self) -> bool:
        """Return Indicator dns active."""
        return self._indicator_data.get('flag1')

    @dns_active.setter
    def dns_active(self, dns_active: bool):
        """Set Indicator dns active."""
        self._indicator_data['flag1'] = self._utils.to_bool(dns_active)

    @property
    def whois_active(self) -> bool:
        """Return Indicator whois active."""
        return self._indicator_data.get('flag2')

    @whois_active.setter
    def whois_active(self, whois_active: bool):
        """Set Indicator whois active."""
        self._indicator_data['flag2'] = self._utils.to_bool(whois_active)


class Mutex(Indicator):
    """ThreatConnect Batch Mutex Object"""

    __slots__ = []

    def __init__(self, mutex: str, **kwargs):
        """Initialize Class Properties.

        Args:
            mutex: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('Mutex', mutex, **kwargs)


class RegistryKey(Indicator):
    """ThreatConnect Batch Registry Key Object"""

    __slots__ = []

    def __init__(self, key_name: str, value_name: str, value_type: str, **kwargs):
        """Initialize Class Properties.

        Args:
            key_name: The key_name value for this Indicator.
            value_name: The value_name value for this Indicator.
            value_type: The value_type value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        summary = self.build_summary(key_name, value_name, value_type)
        super().__init__('Registry Key', summary, **kwargs)


class URL(Indicator):
    """ThreatConnect Batch URL Object"""

    __slots__ = []

    def __init__(self, text: str, **kwargs):
        """Initialize Class Properties.

        Args:
            text: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('URL', text, **kwargs)


class UserAgent(Indicator):
    """ThreatConnect Batch User Agent Object"""

    __slots__ = []

    def __init__(self, text: str, **kwargs):
        """Initialize Class Properties.

        Args:
            text: The value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): The date timestamp the Indicator was created.
            last_modified (str, kwargs): The date timestamp the Indicator was last modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__('User Agent', text, **kwargs)


class FileAction:
    """ThreatConnect Batch FileAction Object"""

    __slots__ = ['_action_data', '_children', 'xid']

    def __init__(self, parent_xid: str, relationship):
        """Initialize Class Properties.

        .. warning:: This code is not complete and may require some update to the API.

        Args:
            parent_xid: The external id of the parent Indicator.
            relationship: ???
        """
        self.xid = str(uuid.uuid4())
        self._action_data = {
            'indicatorXid': self.xid,
            'relationship': relationship,
            'parentIndicatorXid': parent_xid,
        }
        self._children = []

    @property
    def data(self) -> dict:
        """Return File Occurrence data."""
        if self._children:
            for child in self._children:
                self._action_data.setdefault('children', []).append(child.data)
        return self._action_data

    def action(self, relationship) -> None:
        """Add a nested File Action."""
        action_obj = FileAction(self.xid, relationship)
        self._children.append(action_obj)

    def __str__(self) -> str:
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)


class FileOccurrence:
    """ThreatConnect Batch FileAction Object."""

    __slots__ = ['_occurrence_data', '_utils']

    def __init__(
        self,
        file_name: Optional[str] = None,
        path: Optional[str] = None,
        date: Optional[str] = None,
    ):
        """Initialize Class Properties

        Args:
            file_name (str, optional): The file name for this occurrence.
            path (str, optional): The file path for this occurrence.
            date (str, optional): The datetime expression for this occurrence.
        """
        self._utils = Utils()
        self._occurrence_data = {}
        if file_name is not None:
            self._occurrence_data['fileName'] = file_name
        if path is not None:
            self._occurrence_data['path'] = path
        if date is not None:
            self._occurrence_data['date'] = self._utils.datetime.format_datetime(
                date, date_format='%Y-%m-%dT%H:%M:%SZ'
            )

    @property
    def data(self) -> dict:
        """Return File Occurrence data."""
        return self._occurrence_data

    @property
    def date(self) -> str:
        """Return File Occurrence date."""
        return self._occurrence_data.get('date')

    @date.setter
    def date(self, date: str):
        """Set File Occurrence date."""
        self._occurrence_data['date'] = self._utils.datetime.format_datetime(
            date, date_format='%Y-%m-%dT%H:%M:%SZ'
        )

    @property
    def file_name(self) -> str:
        """Return File Occurrence file name."""
        return self._occurrence_data.get('fileName')

    @file_name.setter
    def file_name(self, file_name: str):
        """Set File Occurrence file name."""
        self._occurrence_data['fileName'] = file_name

    @property
    def path(self) -> str:
        """Return File Occurrence path."""
        return self._occurrence_data.get('path')

    @path.setter
    def path(self, path: str):
        """Set File Occurrence path."""
        self._occurrence_data['path'] = path

    def __str__(self) -> str:
        """Return string represtentation of object."""
        return json.dumps(self.data, indent=4)
