# -*- coding: utf-8 -*-
"""ThreatConnect Threat Intelligence Module"""
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
from tcex.tcex_ti.mappings.task import Task
from tcex.tcex_ti.mappings.filters import Filters
from tcex.tcex_ti.mappings.group.group_types.event import Event
from tcex.tcex_ti.mappings.group.group_types.incident import Incident
from tcex.tcex_ti.mappings.group.group_types.intrusion_set import IntrusionSet
from tcex.tcex_ti.mappings.group.group_types.report import Report
from tcex.tcex_ti.mappings.group.group_types.signature import Signature
from tcex.tcex_ti.mappings.group.group_types.threat import Threat
from tcex.tcex_ti.mappings.victim import Victim
from tcex.tcex_ti.mappings.tag import Tag
from tcex.tcex_ti.mappings.group.tcex_ti_group import Group
from tcex.tcex_ti.mappings.tcex_ti_owner import Owner

p = inflect.engine()

# import local modules for dynamic reference
module = __import__(__name__)


class TcExTi(object):
    """ThreatConnect Threat Intelligence Module"""

    def __init__(self, tcex):
        """
        Args:
            tcex (obj): An instance of TcEx.
        """
        self.tcex = tcex
        self._custom_indicator_classes = {}
        self._gen_indicator_class()

    def address(self, ip, owner=None, **kwargs):
        """
        Create the Address TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            ip:
            **kwargs:

        Return:

        """
        return Address(self.tcex, ip, owner=owner, **kwargs)

    def url(self, url, owner=None, **kwargs):
        """
        Create the URL TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            url:
            **kwargs:

        Return:

        """
        return URL(self.tcex, url, owner=owner, **kwargs)

    def email_address(self, address, owner=None, **kwargs):
        """
        Create the Email Address TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            address:
            **kwargs:

        Return:

        """
        return EmailAddress(self.tcex, address, owner=owner, **kwargs)

    def file(self, owner=None, **kwargs):
        """
        Create the File TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            **kwargs:

        Return:

        """
        return File(self.tcex, owner=owner, **kwargs)

    def host(self, hostname, owner=None, **kwargs):
        """
        Create the Host TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            hostname:
            **kwargs:

        Return:

        """
        return Host(self.tcex, hostname, owner=owner, **kwargs)

    def filters(self):
        """ Creates a Filters TI object """
        return Filters(self.tcex)

    def indicator(self, indicator_type=None, owner=None, **kwargs):
        """
        Create the Indicator TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            indicator_type:
            **kwargs:

        Return:

        """
        if not indicator_type:
            return Indicator(self.tcex, None, owner=owner, **kwargs)

        upper_indicator_type = indicator_type.upper()

        indicator = None
        if upper_indicator_type == 'ADDRESS':
            indicator = Address(self.tcex, kwargs.pop('ip', None), owner=owner, **kwargs)
        elif upper_indicator_type == 'EMAIL ADDRESS':
            indicator = EmailAddress(self.tcex, kwargs.pop('address', None), owner=owner, **kwargs)
        elif upper_indicator_type == 'FILE':
            indicator = File(self.tcex, owner=owner, **kwargs)
        elif upper_indicator_type == 'HOST':
            indicator = Host(self.tcex, kwargs.pop('hostname', None), owner=owner, **kwargs)
        elif upper_indicator_type == 'URL':
            indicator = URL(self.tcex, kwargs.pop('url', None), owner=owner, **kwargs)
        # elif upper_indicator_type == 'ASN':
        #     indicator = ASN(self.tcex, kwargs.pop('AS Number', None), owner=owner, **kwargs)
        # elif upper_indicator_type == 'CIDR':
        #     indicator = CIDR(self.tcex, kwargs.pop('Block', None), owner=owner, **kwargs)
        # elif upper_indicator_type == 'MUTEX':
        #     indicator = Mutex(self.tcex, kwargs.pop('Mutex', None), owner=owner, **kwargs)
        # elif upper_indicator_type == 'REGISTRY KEY':
        #     indicator = RegistryKey(
        #         self.tcex,
        #         kwargs.pop('Key Name', None),
        #         kwargs.pop('Value Name', None),
        #         kwargs.pop('Value Type', None),
        #         owner=owner,
        #         **kwargs
        #     )
        # elif upper_indicator_type == 'USER AGENT':
        #     indicator = UserAgent(
        #         self.tcex, kwargs.pop('User Agent String', None), owner=owner, **kwargs
        #     )
        else:
            try:
                if upper_indicator_type in self._custom_indicator_classes.keys():
                    custom_indicator_details = self._custom_indicator_classes[upper_indicator_type]
                    value_fields = custom_indicator_details.get('value_fields')
                    c = getattr(module, indicator_type.replace(' ', ''))
                    if len(value_fields) == 1:
                        indicator = c(
                            self.tcex, kwargs.pop(value_fields[0], None), owner=owner, **kwargs
                        )
                    elif len(value_fields) == 2:
                        indicator = c(
                            self.tcex,
                            kwargs.pop(value_fields[0], None),
                            kwargs.pop(value_fields[1], None),
                            owner=owner,
                            **kwargs
                        )
                    elif len(value_fields) == 3:
                        indicator = c(
                            self.tcex,
                            kwargs.pop(value_fields[0], None),
                            kwargs.pop(value_fields[1], None),
                            kwargs.pop(value_fields[2], None),
                            owner=owner,
                            **kwargs
                        )
            except Exception:
                return None
        return indicator

    def group(self, group_type=None, owner=None, **kwargs):
        """
        Create the Group TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            group_type:
            **kwargs:

        Return:

        """

        group = None
        if not group_type:
            return Group(self.tcex, None, None, owner=owner, **kwargs)

        name = kwargs.pop('name', None)
        group_type = group_type.upper()
        if group_type == 'ADVERSARY':
            group = Adversary(self.tcex, name, owner=owner, **kwargs)
        if group_type == 'CAMPAIGN':
            group = Campaign(self.tcex, name, owner=owner, **kwargs)
        if group_type == 'DOCUMENT':
            group = Document(self.tcex, name, kwargs.pop('file_name', None), owner=owner, **kwargs)
        if group_type == 'EVENT':
            group = Event(self.tcex, name, owner=owner, **kwargs)
        if group_type == 'EMAIL':
            group = Email(
                self.tcex,
                name,
                kwargs.pop('to', None),
                kwargs.pop('from_addr', None),
                kwargs.pop('subject', None),
                kwargs.pop('body', None),
                kwargs.pop('header', None),
                owner=owner,
                **kwargs
            )
        if group_type == 'INCIDENT':
            group = Incident(self.tcex, name, owner=owner, **kwargs)
        if group_type == 'INTRUSION SET':
            group = IntrusionSet(self.tcex, name, owner=owner, **kwargs)
        if group_type == 'REPORT':
            group = Report(self.tcex, name, owner=owner, **kwargs)
        if group_type == 'SIGNATURE':
            group = Signature(
                self.tcex,
                name,
                kwargs.pop('file_name', None),
                kwargs.pop('file_type', None),
                kwargs.pop('file_text', None),
                owner=owner,
                **kwargs
            )
        if group_type == 'THREAT':
            group = Threat(self.tcex, name, owner=owner, **kwargs)
        if group_type == 'TASK':
            group = Task(
                self.tcex,
                name,
                kwargs.pop('status', 'Not Started'),
                kwargs.pop('due_date', None),
                kwargs.pop('reminder_date', None),
                kwargs.pop('escalation_date', None),
                owner=owner,
                **kwargs
            )
        return group

    def adversary(self, name, owner=None, **kwargs):
        """
        Create the Adversary TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:

        Return:

        """
        return Adversary(self.tcex, name, owner=owner, **kwargs)

    def campaign(self, name, owner=None, **kwargs):
        """
        Create the Campaign TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:

        Return:

        """
        return Campaign(self.tcex, name, owner=owner, **kwargs)

    def document(self, name, file_name, owner=None, **kwargs):
        """
        Create the Document TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            file_name:
            **kwargs:

        Return:

        """
        return Document(self.tcex, name, file_name, owner=owner, **kwargs)

    def event(self, name, owner=None, **kwargs):
        """
        Create the Event TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Event(self.tcex, name, owner=owner, **kwargs)

    def email(self, name, to, from_addr, subject, body, header, owner=None, **kwargs):
        """
        Create the Email TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            to:
            from_addr:
            name:
            subject:
            header:
            body:
            **kwargs:

        Return:

        """
        return Email(self.tcex, name, to, from_addr, subject, body, header, owner=owner, **kwargs)

    def incident(self, name, owner=None, **kwargs):
        """
        Create the Incident TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:

        Return:

        """
        return Incident(self.tcex, name, owner=owner, **kwargs)

    def intrusion_sets(self, name, owner=None, **kwargs):
        """
        Create the Intrustion Set TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:

        Return:

        """
        return IntrusionSet(self.tcex, name, owner=owner, **kwargs)

    def report(self, name, owner=None, **kwargs):
        """
        Create the Report TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:

        Return:

        """
        return Report(self.tcex, name, owner=owner, **kwargs)

    def signature(self, name, file_name, file_type, file_content, owner=None, **kwargs):
        """
        Create the Signature TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            file_content:
            file_name:
            file_type:
            name:
            **kwargs:

        Return:

        """
        return Signature(self.tcex, name, file_name, file_type, file_content, owner=owner, **kwargs)

    def threat(self, name, owner=None, **kwargs):
        """
        Create the Threat TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:

        Return:

        """
        return Threat(self.tcex, name, owner=owner, **kwargs)

    def victim(self, name, owner=None, **kwargs):
        """
        Create the Victim TI object.

        Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:

        Return:

        """
        return Victim(self.tcex, name, owner=owner, **kwargs)

    def tag(self, name):
        """
        Create the Tag TI object.

        Args:
            name:

        Return:

        """
        return Tag(self.tcex, name)

    def owner(self):
        """
        Create the Owner object.

        Return:

        """
        return Owner(self.tcex)

    def entities(self, tc_data, resource_type):
        """
        Yields a entity. Takes both a list of indicators/groups or a individual
        indicator/group response.

        example formats

        .. code-block:: javascript

            {
                "status": "Success",
                "data": {
                    "resultCount": 984240,
                    "address": [
                        {
                            "id": 4222035,
                            "ownerName": "System",
                            "dateAdded": "2019-03-28T10:32:05-04:00",
                            "lastModified": "2019-03-28T11:02:46-04:00",
                            "rating": 4,
                            "confidence": 90,
                            "threatAssessRating": 4,
                            "threatAssessConfidence": 90,
                            "webLink": "{host}/auth/indicators/details/address.xhtml?
                                        address=221.123.32.14",
                            "ip": "221.123.32.14"
                        },
                        {
                            "id": 4221517,
                            "ownerName": "System",
                            "dateAdded": "2018-11-05T14:24:54-05:00",
                            "lastModified": "2019-03-07T12:38:36-05:00",
                            "threatAssessRating": 0,
                            "threatAssessConfidence": 0,
                            "webLink": "{host}/auth/indicators/details/address.xhtml?
                                        address=221.123.32.12",
                            "ip": "221.123.32.12"
                        }
                    ]
                }
            }

        or:

        .. code-block:: javascript

            {
                "status": "Success",
                "data": {
                    "address": {
                        "id": 4222035,
                        "owner": {
                            "id": 1,
                            "name": "System",
                            "type": "Organization"
                        },
                        "dateAdded": "2019-03-28T10:32:05-04:00",
                        "lastModified": "2019-03-28T11:02:46-04:00",
                        "rating": 4,
                        "confidence": 90,
                        "threatAssessRating": 4,
                        "threatAssessConfidence": 90,
                        "webLink": "{host}/auth/indicators/details/address.xhtml?
                                    address=221.123.32.14",
                        "ip": "221.123.32.14"
                    }
                }
            }

        Args:
            json_response:

        Yields:

        """
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for d in tc_data:
            entity = {'id': d.get('id'), 'webLink': d.get('webLink')}
            values = []
            value = None
            if resource_type in self.tcex.group_types:
                r = self.tcex.ti.group(group_type=resource_type, name=d.get('name'))
                value = d.get('name')
            elif resource_type in self.tcex.indicator_types:
                r = self.tcex.ti.indicator(indicator_type=resource_type)
                r._set_unique_id(d)
                value = r.unique_id
            elif resource_type.lower() in ['victim']:
                r = self.tcex.ti.victim(d.get('name'))
                value = d.get('name')
            else:
                self.tcex.handle_error(925, ['type', 'entities', 'type', 'type', resource_type])

            if 'summary' in d:
                values.append(d.get('summary'))
            else:
                values.append(value)
            entity['value'] = ' : '.join(values)

            if r.is_group() or r.is_indicator():
                if 'owner' in d:
                    entity['ownerName'] = d['owner']['name']
                else:
                    entity['ownerName'] = d.get('ownerName')
                entity['dateAdded'] = d.get('dateAdded')

            if r.is_victim():
                entity['ownerName'] = d.get('org')

            if r.is_indicator():
                entity['confidence'] = d.get('confidence')
                entity['rating'] = d.get('rating')
                entity['threatAssessConfidence'] = d.get('threatAssessConfidence')
                entity['threatAssessRating'] = d.get('threatAssessRating')
                entity['dateLastModified'] = d.get('lastModified')
            # type
            if d.get('type') is not None:
                entity['type'] = d.get('type')
            else:
                entity['type'] = resource_type

            yield entity

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

            if not value_fields:
                continue

            # Add Class for each Custom Indicator type to this module
            custom_class = custom_indicator_class_factory(
                entry.get('name'),
                entry.get('apiEntity'),
                entry.get('apiBranch'),
                Indicator,
                value_fields,
            )

            custom_indicator_data = {
                'branch': entry.get('apiBranch'),
                'entry': entry.get('apiEntry'),
                'value_fields': value_fields,
            }
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
        def method_1(value1, owner=None, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, owner=owner, **kwargs)

        def method_2(value1, value2, owner=None, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, value2, owner=owner, **kwargs)

        def method_3(value1, value2, value3, owner=None, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, value2, value3, owner=owner, **kwargs)

        method = locals()['method_{}'.format(value_count)]
        setattr(self, method_name, method)
