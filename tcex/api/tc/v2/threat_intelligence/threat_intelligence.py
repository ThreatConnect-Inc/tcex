"""TcEx Framework Module"""
# standard library
import logging
from functools import lru_cache
from typing import cast

# third-party
from requests import Response, Session  # TYPE-CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.filters import Filters
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.adversary import Adversary
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.attack_pattern import AttackPattern
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.campaign import Campaign
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.course_of_action import (
    CourseOfAction,
)
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.document import Document
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.email import Email
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.event import Event
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.incident import Incident
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.intrusion_set import IntrusionSet
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.malware import Malware
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.report import Report
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.signature import Signature
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.tactic import Tactic
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.threat import Threat
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.tool import Tool
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.vulnerability import Vulnerability
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator import (
    Indicator,
    custom_indicator_class_factory,
)
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator_type.address import Address
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator_type.email_address import (
    EmailAddress,
)
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator_type.file import File
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator_type.host import Host
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator_type.url import URL
from tcex.api.tc.v2.threat_intelligence.mapping.owner import Owner
from tcex.api.tc.v2.threat_intelligence.mapping.tag import Tag
from tcex.api.tc.v2.threat_intelligence.mapping.tags import Tags
from tcex.api.tc.v2.threat_intelligence.mapping.task import Task
from tcex.api.tc.v2.threat_intelligence.mapping.victim import Victim
from tcex.exit.error_code import TcExErrorCode
from tcex.logger.trace_logger import TraceLogger
from tcex.util import Util

# import local modules for dynamic reference
module = __import__(__name__)

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class ThreatIntelligence:
    """ThreatConnect Threat Intelligence Module"""

    def __init__(self, session_tc: Session):
        """Initialize instance properties."""
        self.session_tc = session_tc

        # properties
        self._custom_indicator_classes = {}
        self.log = _logger
        self.util = Util()

        # generate custom ioc classes
        self._gen_indicator_class()

    @property
    @lru_cache
    def _error_codes(self) -> TcExErrorCode:
        """Return TcEx error codes."""
        return TcExErrorCode()

    @property
    def _group_types(self) -> list:
        """Return all defined ThreatConnect Group types.

        Returns:
            (list): A list of ThreatConnect Group types.
        """
        return [
            'Adversary',
            'Campaign',
            'Document',
            'Email',
            'Event',
            'Incident',
            'Intrusion Set',
            'Signature',
            'Report',
            'Threat',
            'Task',
            'Attack Pattern',
            'Malware',
            'Vulnerability',
            'Tactic',
            'Tool',
            'Course of Action',
        ]

    @property
    def _group_types_data(self) -> dict:
        """Return supported ThreatConnect Group types."""
        return {
            'Adversary': {'apiBranch': 'adversaries', 'apiEntity': 'adversary'},
            'Campaign': {'apiBranch': 'campaigns', 'apiEntity': 'campaign'},
            'Document': {'apiBranch': 'documents', 'apiEntity': 'document'},
            'Email': {'apiBranch': 'emails', 'apiEntity': 'email'},
            'Event': {'apiBranch': 'events', 'apiEntity': 'event'},
            'Incident': {'apiBranch': 'incidents', 'apiEntity': 'incident'},
            'Intrusion Set': {'apiBranch': 'intrusionSets', 'apiEntity': 'intrusionSet'},
            'Report': {'apiBranch': 'reports', 'apiEntity': 'report'},
            'Signature': {'apiBranch': 'signatures', 'apiEntity': 'signature'},
            'Threat': {'apiBranch': 'threats', 'apiEntity': 'threat'},
            'Task': {'apiBranch': 'tasks', 'apiEntity': 'task'},
            'Attack Pattern': {'apiBranch': 'attackpatterns', 'apiEntity': 'attackPattern'},
            'Malware': {'apiBranch': 'malware', 'apiEntity': 'malware'},
            'Vulnerability': {'apiBranch': 'vulnerabilities', 'apiEntity': 'vulnerability'},
            'Tactic': {'apiBranch': 'tactics', 'apiEntity': 'tactic'},
            'Tool': {'apiBranch': 'tools', 'apiEntity': 'tool'},
            'Course of Action': {'apiBranch': 'coursesofaction', 'apiEntity': 'courseofAction'},
        }

    @property
    @lru_cache
    def _indicator_types_data(self) -> dict:
        """Return ThreatConnect indicator types data.

        Retrieve the data from the API if it hasn't already been retrieved.

        Returns:
            (dict): A dictionary of ThreatConnect Indicator data.
        """
        _indicator_types_data = {}

        # retrieve data from API
        r = self.session_tc.get('/v2/types/indicatorTypes')

        # TODO: use handle error instead
        if not r.ok:
            raise RuntimeError('Could not retrieve indicator types from ThreatConnect API.')

        for itd in r.json().get('data', {}).get('indicatorType'):
            _indicator_types_data[itd.get('name')] = itd

        return _indicator_types_data

    def _handle_error(
        self, code: int, message_values: list | None = None, raise_error: bool = True
    ):
        """Raise RuntimeError

        Args:
            code: The error code from API or SDK.
            message_values: The error message from API or SDK.
            raise_error: Raise a Runtime error. Defaults to True.

        Raises:
            RuntimeError: Raised a defined error.
        """
        try:
            if message_values is None:
                message_values = []
            message = self._error_codes.message(code).format(*message_values)
            self.log.error(f'Error code: {code}, {message}')
        except AttributeError:
            self.log.error(f'Incorrect error code provided ({code}).')
            raise RuntimeError(100, 'Generic Failure, see logs for more details.')
        except IndexError:
            self.log.error(
                f'Incorrect message values provided for error code {code} ({message_values}).'
            )
            raise RuntimeError(100, 'Generic Failure, see logs for more details.')
        if raise_error:
            raise RuntimeError(code, message)

    def address(self, **kwargs):
        """Return an Address TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            ip (str, kwargs): [Required for Create] The IP value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            last_modified (str, kwargs): [Read-Only] The date timestamp the Indicator was last
                modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.

        Returns:
            obj: An instance of Address.
        """
        return Address(self, **kwargs)

    def url(self, **kwargs):
        """Create the URL TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            text (str, kwargs): [Required for Create] The URL value for this Indicator.

        Return:
            obj: An instance of URL.
        """
        return URL(self, **kwargs)

    def email_address(self, **kwargs):
        """Create the Email Address TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            address (str, kwargs): [Required for Create] The Email Address value for this Indicator.

        Return:
            obj: An instance of EmailAddress.
        """
        return EmailAddress(self, **kwargs)

    def file(self, **kwargs):
        """Create the File TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            obj: An instance of File.
        """
        return File(self, **kwargs)

    def host(self, **kwargs):
        """Create the Host TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            hostname (str, kwargs): [Required for Create] The Host value for this Indicator.

        Return:
            obj: An instance of Host.
        """
        return Host(self, **kwargs)

    @staticmethod
    def filters():
        """Create a Filters TI object"""
        return Filters()

    def indicator(self, indicator_type=None, owner=None, **kwargs):
        """Return an TI object.

        Args:
            indicator_type (str): The indicator type.
            owner (str): The name for this Group. Default to default Org when not provided
            **kwargs: Additional keyword arguments.

        Keyword Args:
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            ip (str, kwargs): [address] The value for this Indicator.
            last_modified (str, kwargs): [Read-Only] The date timestamp the Indicator was last
                modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.

        Returns:
            obj: An instance of Indicator or specific indicator type.
        """
        if not indicator_type:
            return Indicator(self, owner=owner, **kwargs)

        indicator_type_map = {
            'address': Address,
            'email address': EmailAddress,
            'emailaddress': EmailAddress,
            'file': File,
            'host': Host,
            'url': URL,
        }

        indicator_type = indicator_type.lower()
        for custom_type in self._custom_indicator_classes:
            for a in dir(module):
                if a.lower() == custom_type.replace(' ', ''):
                    indicator_type_map[custom_type.lower()] = getattr(module, a)

        if indicator_type not in indicator_type_map:
            raise RuntimeError(f'Invalid indicator type "{indicator_type}" provided.')

        # update kwargs
        kwargs['owner'] = owner

        # return correct indicator object
        indicator_object = indicator_type_map[indicator_type]
        return indicator_object(self, **kwargs)

    def group(self, group_type=None, owner=None, **kwargs):
        """Create the Group TI object.

        Args:
            group_type: The type of group object.
            owner (str): The ThreatConnect owner name.
            **kwargs: Additional keyword arguments.
        """
        if not group_type:
            return Group(self, owner=owner, **kwargs)

        group_type_map = {
            'adversary': Adversary,
            'campaign': Campaign,
            'document': Document,
            'event': Event,
            'email': Email,
            'incident': Incident,
            'intrusion set': IntrusionSet,
            'report': Report,
            'signature': Signature,
            'threat': Threat,
            'attack pattern': AttackPattern,
            'malware': Malware,
            'vulnerability': Vulnerability,
            'tactic': Tactic,
            'tool': Tool,
            'course of action': CourseOfAction,
        }

        # if "name" is not in kwargs
        if kwargs.get('name') is None:
            kwargs['name'] = None

        group_type = group_type.lower()
        if group_type not in group_type_map:
            raise RuntimeError(f'Invalid group type "{group_type}" provided.')

        # update kwargs
        kwargs['owner'] = owner

        # return correct group object
        group_object = group_type_map[group_type]
        return group_object(self, **kwargs)

    def attack_pattern(self, **kwargs):
        """Create the Attack Pattern TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.AttackPattern: An instance of AttackPattern.
        """
        return AttackPattern(self, **kwargs)

    def malware(self, **kwargs):
        """Create the Malware TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.Malware: An instance of Malware.
        """
        return Malware(self, **kwargs)

    def vulnerability(self, **kwargs):
        """Create the Vulnerability TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.Vulnerability: An instance of Vulnerability.
        """
        return Vulnerability(self, **kwargs)

    def tactic(self, **kwargs):
        """Create the Tactic TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.Tactic: An instance of Tactic.
        """
        return Tactic(self, **kwargs)

    def tool(self, **kwargs):
        """Create the Tool TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.Tool: An instance of Tool.
        """
        return Tool(self, **kwargs)

    def course_of_action(self, **kwargs):
        """Create the Course of Action TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.CourseOfAction: An instance of CourseOfAction.
        """
        return CourseOfAction(self, **kwargs)

    def adversary(self, **kwargs):
        """Create the Adversary TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.Adversary: An instance of Adversary.
        """
        return Adversary(self, **kwargs)

    def campaign(self, **kwargs):
        """Create the Campaign TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            first_seen (str, kwargs): The first seen datetime expression for this Group.

        Return:
            ti.Campaign: An instance of Campaign.
        """
        return Campaign(self, **kwargs)

    def document(self, **kwargs):
        """Create the Document TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            file_name (str, kwargs): The name for the attached file for this Group.
            malware (bool, kwargs): If true the file is considered malware.
            password (bool, kwargs): If malware is true a password for the zip archive is required.

        Return:
            ti.Document: An instance of Document.
        """
        return Document(self, **kwargs)

    def email(self, **kwargs):
        """Create the Email TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            body (str): The body for this Email.
            from_addr (str, kwargs): The **from** address for this Email.
            header (str): The header for this Email.
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            subject (str): The subject for this Email.
            to (str, kwargs): The **to** address for this Email.

        Return:
            ti.Email: An instance of Email.
        """
        return Email(self, **kwargs)

    def event(self, **kwargs):
        """Create the Event TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            event_date (str, kwargs): The event "event date" datetime expression for this Group.
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            status (str, kwargs): The status for this Group.

        Return:
            ti.Event: An instance of Event.
        """
        return Event(self, **kwargs)

    def incident(self, **kwargs):
        """Create the Incident TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            event_date (str, kwargs): The incident event date expression for this Group.
            name (str, kwargs): [Required for Create] The name for this Group.
            status (str, kwargs): The status for this Group.

        Return:
            ti.Incident: An instance of Incident.
        """
        return Incident(self, **kwargs)

    def intrusion_set(self, **kwargs):
        """Create the Intrusion Set TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided

        Return:
            ti.IntrusionSet: An instance of IntrusionSet.
        """
        return IntrusionSet(self, **kwargs)

    def report(self, **kwargs):
        """Create the Report TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str): The ThreatConnect owner name.
            name:
            **kwargs:
        """
        return Report(self, **kwargs)

    def signature(self, **kwargs):
        """Create the Signature TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str): The ThreatConnect owner name.
            name (str): The name for this Group.
            file_name (str): The name for the attached signature for this Group.
            file_type (str): The signature type for this Group.
            file_text (str): The signature content for this Group.
            **kwargs:

        Return:
            obj: An instance of Signature.
        """
        return Signature(self, **kwargs)

    def task(self, **kwargs):
        """Create the Task TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            name (str, kwargs): [Required for Create] The name for this Group.
            owner (str, kwargs): The name for this Group. Default to default Org when not provided
            status (str, kwargs): Not started, In Progress, Completed, Waiting on Someone, Deferred
            due_date (str, kwargs): Converted to %Y-%m-%dT%H:%M:%SZ date format
            reminder_date (str, kwargs): Converted to %Y-%m-%dT%H:%M:%SZ date format
            escalation_date (str, kwargs): Converted to %Y-%m-%dT%H:%M:%SZ date format

        Return:
            obj: An instance of Task
        """
        return Task(self, **kwargs)

    def threat(self, **kwargs):
        """Create the Threat TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str): The ThreatConnect owner name.
            name:
        """
        return Threat(self, **kwargs)

    def victim(self, **kwargs):
        """Create the Victim TI object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            owner (str): The ThreatConnect owner name.
            name:
        """
        return Victim(self, **kwargs)

    def tags(self):
        """Create the Tag TI object."""
        return Tags(self)

    def tag(self, name):
        """Create the Tag TI object."""
        return Tag(self, name)

    def owner(self):
        """Create the Owner object."""
        return Owner(self)

    def create_entity(self, entity, owner):
        """Given a Entity and a Owner, creates a indicator/group in ThreatConnect"""
        attributes = entity.pop('attribute', [])
        associations = entity.pop('associations', [])
        security_labels = entity.pop('securityLabel', [])
        tags = entity.pop('tag', [])
        entity_type = entity.pop('type', '').lower()
        file_content = None
        if entity_type in ['document', 'report']:
            file_content = entity.pop('file_content', None) or entity.pop('fileContent', None)
        try:
            ti = cast(Indicator, self.indicator(entity_type, owner, **entity))
            if entity.get('falsePositive'):
                ti.add_false_positive()
        except Exception:
            if entity_type in ['victim']:
                ti = self.victim(owner=owner, **entity)
            else:
                entity['name'] = entity.pop('summary', None)
                if entity_type in ['task']:
                    ti = self.task(owner=owner, **entity)
                else:
                    ti = self.group(entity_type, owner, **entity)
        r = cast(Response, ti.create())
        if file_content and entity_type in ['document', 'report']:
            ti = cast(Document | Report, ti)
            ti.file_content(file_content)

        data: dict[str, int | list | str] = {'status_code': r.status_code}
        if r.ok:
            data.update(r.json().get('data', {}))
            data['main_type'] = ti.type
            data['sub_type'] = ti.api_sub_type
            data['api_type'] = ti.api_sub_type
            data['api_entity'] = ti.api_entity
            data['api_branch'] = ti.api_branch
            data['owner'] = owner
            data['attributes'] = []
            data['tags'] = []
            data['security_labels'] = []
            data['associations'] = []
        else:
            return None

        for attribute in attributes:
            r = ti.add_attribute(attribute.get('type'), attribute.get('value'))
            attribute_data = {'status_code': r.status_code}
            if r.ok:
                attribute_data.update(r.json().get('attribute', {}))
            data['attributes'].append(attribute_data)
        for tag in tags:
            r = cast(Response, ti.add_tag(tag))
            tag_response = {'status_code': r.status_code}
            data['tags'].append(tag_response)
        for label in security_labels:
            r = cast(Response, ti.add_label(label))
            label_response = {'status_code': r.status_code}
            data['security_labels'].append(label_response)
        for association in associations:
            association_target = self.indicator(
                association.pop('type', None), association.pop('owner', None), **association
            )
            if not association_target:
                association_target = self.group(
                    association.pop('type', None), association.pop('owner', None), **association
                )
            r = cast(Response, ti.add_association(association_target))
            association_response = {'status_code': r.status_code}
            if r.ok:
                association_response.update(r.json().get('association', {}))
            data['associations'].append(association_response)

        return data

    def create_entities(self, entities, owner):
        """Create a indicator/group in TC based on the given entity's

        Args:
            entities: The entity to create.
            owner: The owner of the entity (
        """
        responses = []
        for entity in entities:
            responses.append(self.create_entity(entity, owner))
        return responses

    def entities(self, tc_data, resource_type):
        """Yield an entity.

        Takes both a list of indicators/groups or a individual indicator/group response.

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
            tc_data: TC data to convert to a entity.
            resource_type: The type of TC data being provided.

        """
        if not isinstance(tc_data, list):
            tc_data = [tc_data]

        for d in tc_data:
            entity = {'id': d.get('id'), 'webLink': d.get('webLink')}
            values = []
            value = None
            keys = d.keys()
            if resource_type.lower() in map(str.lower, self._group_types):
                # @bpurdy - is this okay?
                # r = self.tcex.api.tc.v2.ti.group(group_type=resource_type, name=d.get('name'))
                r = self.group(group_type=resource_type, name=d.get('name'))
                value = d.get('name')
            elif resource_type.lower() in map(str.lower, self._indicator_types_data):
                # @bpurdy - is this okay?
                # r = self.tcex.api.tc.v2.ti.indicator(indicator_type=resource_type)
                r = self.indicator(indicator_type=resource_type)
                r._set_unique_id(d)
                value = r.unique_id
            elif resource_type.lower() in ['victim']:
                r = self.victim(name=d.get('name'))
                value = d.get('name')
            else:
                self._handle_error(925, ['type', 'entities', 'type', 'type', resource_type])
                continue

            if 'summary' in d:
                values.append(d.get('summary'))
            else:
                r = cast(Indicator, r)
                if resource_type.lower() in ['file']:
                    value = r.build_summary(d.get('md5'), d.get('sha1'), d.get('sha256'))
                values.append(r.fully_decode_uri(value))
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
                if 'whoisActive' in keys:
                    entity['whoisActive'] = d.get('whoisActive')
                if 'dnsActive' in keys:
                    entity['dnsActive'] = d.get('dnsActive')

            if r.is_task():
                entity['status'] = d.get('status')
                entity['escalated'] = d.get('escalated')
                entity['reminded'] = d.get('reminded')
                entity['overdue'] = d.get('overdue')
                entity['dueDate'] = d.get('dueDate', None)
                entity['reminderDate'] = d.get('reminderDate', None)
                entity['escalationDate'] = d.get('escalationDate', None)
                if d.get('xid'):
                    entity['xid'] = d.get('xid')
            if r.is_group():
                if 'xid' in keys:
                    entity['xid'] = d.get('xid')
                if 'firstSeen' in keys:
                    entity['firstSeen'] = d.get('firstSeen')
                if 'fileName' in keys:
                    entity['fileName'] = d.get('fileName')
                if 'fileType' in keys:
                    entity['fileType'] = d.get('fileType')
                if 'fileSize' in keys:
                    entity['fileSize'] = d.get('fileSize')
                if 'eventDate' in keys:
                    entity['eventDate'] = d.get('eventDate')
                if 'status' in keys:
                    entity['status'] = d.get('status')
                if 'to' in keys:
                    entity['to'] = d.get('to')
                if 'from' in keys:
                    entity['from'] = d.get('from')
                if 'subject' in keys:
                    entity['subject'] = d.get('subject')
                if 'score' in keys:
                    entity['score'] = d.get('score')
                if 'header' in keys:
                    entity['header'] = d.get('header')
                if 'body' in keys:
                    entity['body'] = d.get('body')
                if 'publishDate' in keys:
                    entity['publishDate'] = d.get('publishDate')
                if r.api_sub_type.lower() in ['signature', 'document', 'report']:
                    r.unique_id = d.get('id')
                    content_response = r.download()  # type: ignore
                    if content_response.ok:
                        entity['fileContent'] = content_response.text
            # get the entity type
            if d.get('type') is not None:
                entity['type'] = d.get('type')
            else:
                entity['type'] = resource_type

            yield entity

    def _gen_indicator_class(self):
        """Generate Custom Indicator Classes."""

        for entry in self._indicator_types_data.values():
            name = entry.get('name')
            class_name = name.replace(' ', '')
            # temp fix for API issue where boolean are returned as strings
            entry['custom'] = self.util.to_bool(entry.get('custom'))

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
            self._custom_indicator_classes[entry.get('name').lower()] = custom_indicator_data

            setattr(module, class_name, custom_class)

            # Add Custom Indicator Method
            self._gen_indicator_method(name, custom_class)

    def _gen_indicator_method(self, name, custom_class):
        """Dynamically generate custom Indicator methods.

        Args:
            name (str): The name of the method.
            custom_class (object): The class to add.
        """
        method_name = name.replace(' ', '_').lower()
        ti = self

        # Add Method for each Custom Indicator class
        def method_1(**kwargs):  # pylint: disable=possibly-unused-variable
            """Add Custom Indicator data to Batch object"""
            return custom_class(ti, **kwargs)

        method = locals()['method_1']
        setattr(self, method_name, method)
