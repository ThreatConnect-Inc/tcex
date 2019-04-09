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

p = inflect.engine()

# import local modules for dynamic reference
module = __import__(__name__)


class TcExTi(object):
    """ThreatConnect Threat Intelligence Module"""

    def __init__(self, tcex):
        """

        Args:
            tcex:

        Return:

        """
        self.tcex = tcex
        self._custom_indicator_classes = {}
        self._gen_indicator_class()

    def address(self, ip, **kwargs):
        """
        Create the Address TI object.

        Args:
            ip:
            **kwargs:

        Return:

        """
        return Address(self.tcex, ip, **kwargs)

    def url(self, url, **kwargs):
        """
        Create the URL TI object.

        Args:
            url:
            **kwargs:

        Return:

        """
        return URL(self.tcex, url, **kwargs)

    def email_address(self, address, **kwargs):
        """
        Create the Email Address TI object.

        Args:
            address:
            **kwargs:

        Return:

        """
        return EmailAddress(self.tcex, address, **kwargs)

    def file(self, **kwargs):
        """
        Create the File TI object.

        Args:
            **kwargs:

        Return:

        """
        return File(self.tcex, **kwargs)

    def host(self, hostname, **kwargs):
        """
        Create the Host TI object.

        Args:
            hostname:
            **kwargs:

        Return:

        """
        return Host(self.tcex, hostname, **kwargs)

    def filters(self):
        """ Creates a Filters TI object """
        return Filters(self.tcex)

    def indicator(self, indicator_type=None, **kwargs):
        """
        Create the Indicator TI object.

        Args:
            indicator_type:
            **kwargs:

        Return:

        """
        if not indicator_type:
            return Indicator(self.tcex, None, **kwargs)

        upper_indicator_type = indicator_type.upper()

        indicator = None
        if upper_indicator_type == 'ADDRESS':
            indicator = Address(self.tcex, kwargs.pop('ip', None), **kwargs)
        elif upper_indicator_type == 'EMAILADDRESS':
            indicator = EmailAddress(self.tcex, kwargs.pop('address', None), **kwargs)
        elif upper_indicator_type == 'FILE':
            indicator = File(self.tcex, **kwargs)
        elif upper_indicator_type == 'HOST':
            indicator = Host(self.tcex, kwargs.pop('hostname', None), **kwargs)
        elif upper_indicator_type == 'URL':
            indicator = URL(self.tcex, kwargs.pop('url', None), **kwargs)
        else:
            try:
                if upper_indicator_type in self._custom_indicator_classes.keys():
                    custom_indicator_details = self._custom_indicator_classes[indicator_type]
                    value_fields = custom_indicator_details.get('value_fields')
                    c = getattr(module, custom_indicator_details.get('branch'))
                    if len(value_fields) == 1:
                        indicator = c(value_fields[0], **kwargs)
                    elif len(value_fields) == 2:
                        indicator = c(value_fields[0], value_fields[1], **kwargs)
                    elif len(value_fields) == 3:
                        indicator = c(value_fields[0], value_fields[2], **kwargs)
            except Exception:
                return None
        return indicator

    def group(self, group_type=None, **kwargs):
        """
        Create the Group TI object.

        Args:
            group_type:
            **kwargs:

        Return:

        """

        group = None
        if not group_type:
            return Group(self.tcex, None, None, **kwargs)

        group_type = group_type.upper()
        if group_type == 'ADVERSARY':
            group = Adversary(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'CAMPAIGN':
            group = Campaign(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'DOCUMENT':
            group = Document(
                self.tcex, kwargs.pop('name', None), kwargs.pop('file_name', None), **kwargs
            )
        if group_type == 'EVENT':
            group = Event(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'EMAIL':
            group = Email(
                self.tcex,
                kwargs.pop('name', None),
                kwargs.pop('to', None),
                kwargs.pop('from_addr', None),
                kwargs.pop('subject', None),
                kwargs.pop('body', None),
                kwargs.pop('header', None),
                **kwargs
            )
        if group_type == 'INCIDENT':
            group = Incident(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'INTRUSION SET':
            group = IntrusionSet(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'REPORT':
            group = Report(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'SIGNATURE':

            group = Signature(
                self.tcex,
                kwargs.pop('name', None),
                kwargs.pop('file_name', None),
                kwargs.pop('file_type', None),
                kwargs.pop('file_text', None),
                **kwargs
            )
        if group_type == 'THREAT':
            group = Threat(self.tcex, kwargs.pop('name', None), **kwargs)
        if group_type == 'TASK':
            group = Task(
                self.tcex,
                kwargs.pop('name', None),
                kwargs.pop('status', 'Not Started'),
                kwargs.pop('due_date', None),
                kwargs.pop('reminder_date', None),
                kwargs.pop('escalation_date', None),
                **kwargs
            )
        return group

    def adversary(self, name, **kwargs):
        """
        Create the Adversary TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Adversary(self.tcex, name, **kwargs)

    def campaign(self, name, **kwargs):
        """
        Create the Campaign TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Campaign(self.tcex, name, **kwargs)

    def document(self, name, file_name, **kwargs):
        """
        Create the Document TI object.

        Args:
            name:
            file_name:
            **kwargs:

        Return:

        """
        return Document(self.tcex, name, file_name, **kwargs)

    def event(self, name, **kwargs):
        """
        Create the Event TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Event(self.tcex, name, **kwargs)

    def email(self, name, to, from_addr, subject, body, header, **kwargs):
        """
        Create the Email TI object.

        Args:
            to:
            from_addr:
            name:
            subject:
            header:
            body:
            **kwargs:

        Return:

        """
        return Email(self.tcex, name, to, from_addr, subject, body, header, **kwargs)

    def incident(self, name, **kwargs):
        """
        Create the Incident TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Incident(self.tcex, name, **kwargs)

    def intrusion_sets(self, name, **kwargs):
        """
        Create the Intrustion Set TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return IntrusionSet(self.tcex, name, **kwargs)

    def report(self, name, **kwargs):
        """
        Create the Report TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Report(self.tcex, name, **kwargs)

    def signature(self, name, file_name, file_type, file_content, **kwargs):
        """
        Create the Signature TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Signature(self.tcex, name, file_name, file_type, file_content, **kwargs)

    def threat(self, name, **kwargs):
        """
        Create the Threat TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Threat(self.tcex, name, **kwargs)

    def victim(self, name, **kwargs):
        """
        Create the Victim TI object.

        Args:
            name:
            **kwargs:

        Return:

        """
        return Victim(self.tcex, name, **kwargs)

    def tag(self, name):
        """
        Create the Tag TI object.

        Args:
            name:

        Return:

        """
        return Tag(self.tcex, name)

    def entities(self, json_response):
        """
        Yields a entity. Takes both a list of indicators/groups or a individual
        indicator/group response.

        example formats:
        {
           "status":"Success",
           "data":{
              "resultCount":984240,
              "address":[
                 {
                    "id":4222035,
                    "ownerName":"System",
                    "dateAdded":"2019-03-28T10:32:05-04:00",
                    "lastModified":"2019-03-28T11:02:46-04:00",
                    "rating":4,
                    "confidence":90,
                    "threatAssessRating":4,
                    "threatAssessConfidence":90,
                    "webLink":"{host}/auth/indicators/details/address.xhtml?address=221.123.32.14",
                    "ip":"221.123.32.14"
                 },
                 {
                    "id":4221517,
                    "ownerName":"System",
                    "dateAdded":"2018-11-05T14:24:54-05:00",
                    "lastModified":"2019-03-07T12:38:36-05:00",
                    "threatAssessRating":0,
                    "threatAssessConfidence":0,
                    "webLink":"{host}/auth/indicators/details/address.xhtml?address=221.123.32.12",
                    "ip":"221.123.32.12"
                 }
              ]
           }
        }

        or:
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
                    "webLink": "{host}/auth/indicators/details/address.xhtml?address=221.123.32.14",
                    "ip": "221.123.32.14"
                }
            }
        }
        Args:
            json_response:

        Yields:

        """
        response_data = json_response.get('data', {})
        api_entity = None
        for key in list(response_data.keys()):
            if key != 'resultCount':
                api_entity = key
            else:
                return
        api_type = self.tcex.get_type_from_api_entity(api_entity)
        response_entities = response_data.get(api_entity, [])
        if not isinstance(response_entities, list):
            response_entities = [response_entities]

        for response_entity in response_entities:
            entity = {}
            data = {}
            temp_entity = None
            value = None
            if api_type in self.tcex.group_types:
                temp_entity = self.tcex.ti.group(
                    group_type=api_type, name=response_data.get('name')
                )
                value = temp_entity.name
            elif api_type in self.tcex.indicator_types:
                temp_entity = self.tcex.ti.indicator(indicator_type=api_type)
                temp_entity._set_unique_id(response_entity)
                value = temp_entity.unique_id
            else:
                self.tcex.handle_error(925, ['type', 'entities', 'type', 'type', api_type])

            confidence = response_entity.get('confidence', None)
            if confidence is not None:
                data['confidence'] = confidence
            rating = response_entity.get('rating', None)
            if rating is not None:
                data['rating'] = rating
            date_added = response_entity.get('dateAdded', None)
            if date_added is not None:
                data['dateAdded'] = date_added
            entity_id = response_entity.get('id', None)
            if entity_id is not None:
                data['id'] = entity_id
            last_modified = response_entity.get('lastModified', None)
            if last_modified is not None:
                data['lastModified'] = last_modified
            owner_name = response_entity.get('owner', {}).get('name', None)
            if owner_name is not None:
                data['ownerName'] = owner_name
            threat_assess_confidence = response_entity.get('threatAssessConfidence', None)
            if threat_assess_confidence is not None:
                data['threatAssessConfidence'] = threat_assess_confidence
            threat_assess_rating = response_entity.get('threatAssessRating', None)
            if threat_assess_rating is not None:
                data['threatAssessRating'] = threat_assess_rating
            if temp_entity.type is not None:
                data['type'] = temp_entity.type
            if value is not None:
                data['value'] = value
            web_link = response_entity.get('webLink')
            if web_link is not None:
                data['webLink'] = web_link
            entity['data_type'] = 'redis'
            entity['variable'] = 'testing'
            entity['data'] = data
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

            if value_fields:
                continue

            class_data = {}
            # Add Class for each Custom Indicator type to this module
            custom_class = custom_indicator_class_factory(
                entry.get('apiBranch'), entry.get('apiEntity'), class_data, value_fields
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
        def method_1(value1, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, **kwargs)

        def method_2(value1, value2, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, value2, **kwargs)

        def method_3(value1, value2, value3, **kwargs):  # pylint: disable=W0641
            """Add Custom Indicator data to Batch object"""
            return custom_class(tcex, value1, value2, value3, **kwargs)

        method = locals()['method_{}'.format(value_count)]
        setattr(self, method_name, method)
