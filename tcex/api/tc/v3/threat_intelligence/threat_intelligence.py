"""TcEx Framework Module"""

# standard library
import logging

# third-party
from requests import Session

# first-party
from tcex.api.tc.util.threat_intel_util import ThreatIntelUtil
from tcex.api.tc.v3.group_attributes.group_attribute import GroupAttribute, GroupAttributes
from tcex.api.tc.v3.groups.group import Group, Groups
from tcex.api.tc.v3.indicator_attributes.indicator_attribute import (
    IndicatorAttribute,
    IndicatorAttributes,
)
from tcex.api.tc.v3.indicators.indicator import Indicator, Indicators
from tcex.api.tc.v3.security_labels.security_label import SecurityLabel
from tcex.api.tc.v3.tags.default_naics_tags import NAICS_TAGS
from tcex.api.tc.v3.tags.mitre_tags import MitreTags
from tcex.api.tc.v3.tags.naics_tags import NAICSTags
from tcex.api.tc.v3.tags.tag import Tags
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.victim_assets.victim_asset import VictimAsset, VictimAssets
from tcex.api.tc.v3.victim_attributes.victim_attribute import VictimAttribute, VictimAttributes
from tcex.api.tc.v3.victims.victim import Victim, Victims
from tcex.logger.trace_logger import TraceLogger
from tcex.pleb.cached_property import cached_property

_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class ThreatIntelligence:
    """Threat Intelligence

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session):
        """Initialize instance properties."""
        self.session = session
        self.log = _logger

    @cached_property
    def ti_utils(self):
        """Return instance of Threat Intel Utils."""
        return ThreatIntelUtil(session_tc=self.session)

    def create_entity(self, entity: dict, owner: str) -> dict | None:
        """Create a CM object provided a dict and owner."""
        entity_type = entity['type'].lower()
        entity_type = entity_type.replace(' ', '_')
        try:
            if entity_type in (type_.lower() for type_ in self.ti_utils.group_types):
                main_type = 'Group'
                obj = self.group(**entity)
            elif entity_type in (type_.lower() for type_ in self.ti_utils.indicator_types):
                main_type = 'Indicator'
                obj = self.indicator(**entity)
            elif entity_type in ['victim']:
                main_type = 'Victim'
                obj = self.victim(**entity)
            else:
                raise RuntimeError(f'Invalid entity type provided for: {entity}')
        except AttributeError:
            return None

        r = obj.create()
        data: dict[str, int | str] = {'status_code': r.status_code}
        if r.ok:
            data.update(r.json().get('data', {}))
            data['main_type'] = main_type
            data['sub_type'] = entity_type
            data['owner'] = owner

        return data

    def group(self, **kwargs) -> Group:
        """Return a instance of Group object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            assignments (None, kwargs): A list of assignees and escalatees associated with this
                group (Task specific).
            associated_groups (Groups, kwargs): A list of groups associated with this group.
            associated_indicators (Indicators, kwargs): A list of indicators associated with this
                group.
            associated_victim_assets (VictimAssets, kwargs): A list of victim assets associated with
                this group.
            attributes (Attributes, kwargs): A list of Attributes corresponding to the Group.
            body (str, kwargs): The email Body.
            due_date (str, kwargs): The date and time that the Task is due.
            escalation_date (str, kwargs): The escalation date and time.
            event_date (str, kwargs): The date and time that the incident or event was first
                created.
            file_name (str, kwargs): The document or signature file name.
            file_text (str, kwargs): The signature file text.
            file_type (str, kwargs): The signature file type.
            first_seen (str, kwargs): The date and time that the campaign was first created.
            from_ (str, kwargs): The email From field.
            handles (AdversaryAssets, kwargs): A list of handle adversary assets associated with
                this group.
            header (str, kwargs): The email Header field.
            id (int, kwargs): The ID of the Group.
            malware (bool, kwargs): Is the document malware?
            name (str, kwargs): The name of the group.
            password (str, kwargs): The password associated with the document (Required if Malware
                is true).
            phone_numbers (AdversaryAssets, kwargs): A list of phone number adversary assets
                associated with this group.
            publish_date (str, kwargs): The date and time that the report was first created.
            reminder_date (str, kwargs): The reminder date and time.
            security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
                Intel item (NOTE: Setting this parameter will replace any existing tag(s) with the
                one(s) specified).
            status (str, kwargs): The status associated with this document, event, task, or incident
                (read only for task, document, and report).
            subject (str, kwargs): The email Subject section.
            tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this
                parameter will replace any existing tag(s) with the one(s) specified).
            to (str, kwargs): The email To field .
            type (str, kwargs): The **type** for the Group.
            urls (AdversaryAssets, kwargs): A list of url adversary assets associated with this
                group.
        """
        return Group(session=self.session, **kwargs)

    def group_attribute(self, **kwargs) -> GroupAttribute:
        """Return a instance of Group Attributes object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            default (bool, kwargs): A flag indicating that this is the default attribute of its type
                within the object. Only applies to certain attribute and data types.
            indicator_id (int, kwargs): Indicator associated with attribute.
            source (str, kwargs): The attribute source.
            type (str, kwargs): The attribute type.
            value (str, kwargs): Attribute value.
        """
        return GroupAttribute(session=self.session, **kwargs)

    def group_attributes(self, **kwargs) -> GroupAttributes:
        """Return a instance of Group Attributes object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Group.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return GroupAttributes(session=self.session, **kwargs)

    def groups(self, **kwargs) -> Groups:
        """Return a instance of Groups object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Group.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return Groups(session=self.session, **kwargs)

    @cached_property
    def naics_tags(self) -> NAICSTags:
        """NAICS Tags"""
        return NAICSTags(naics_tags=NAICS_TAGS)

    def indicator(self, **kwargs) -> Indicator:
        """Return a instance of Group object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            active (bool, kwargs): Is the indicator active?
            active_locked (bool, kwargs): Lock the indicator active value?
            address (str, kwargs): The email address associated with this indicator (EmailAddress
                specific summary field).
            associated_groups (Groups, kwargs): A list of groups that this indicator is associated
                with.
            associated_indicators (Indicators, kwargs): A list of indicators associated with this
                indicator.
            attributes (Attributes, kwargs): A list of Attributes corresponding to the Indicator.
            confidence (int, kwargs): The indicator threat confidence.
            description (str, kwargs): The indicator description text.
            dns_active (bool, kwargs): Is dns active for the indicator?
            host_name (str, kwargs): The host name of the indicator (Host specific summary field).
            ip (str, kwargs): The ip address associated with this indicator (Address specific
                summary field).
            md5 (str, kwargs): The md5 associated with this indicator (File specific summary field).
            private_flag (bool, kwargs): Is this indicator private?
            rating (int, kwargs): The indicator threat rating.
            security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
                Intel item (NOTE: Setting this parameter will replace any existing tag(s) with the
                one(s) specified).
            sha1 (str, kwargs): The sha1 associated with this indicator (File specific summary
                field).
            sha256 (str, kwargs): The sha256 associated with this indicator (File specific summary
                field).
            size (int, kwargs): The size of the file.
            source (str, kwargs): The source for this indicator.
            tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this
                parameter will replace any existing tag(s) with the one(s) specified).
            text (str, kwargs): The url text value of the indicator (Url specific summary field).
            type (str, kwargs): The **type** for the Indicator.
            value1 (str, kwargs): Custom Indicator summary field value1.
            value2 (str, kwargs): Custom Indicator summary field value2.
            value3 (str, kwargs): Custom Indicator summary field value3.
            whois_active (bool, kwargs): Is whois active for the indicator?
        """
        return Indicator(session=self.session, **kwargs)

    def indicator_attribute(self, **kwargs) -> IndicatorAttribute:
        """Return a instance of Case Attributes object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            default (bool, kwargs): A flag indicating that this is the default attribute of its type
                within the object. Only applies to certain attribute and data types.
            indicator_id (int, kwargs): Indicator associated with attribute.
            source (str, kwargs): The attribute source.
            type (str, kwargs): The attribute type.
            value (str, kwargs): Attribute value.
        """
        return IndicatorAttribute(session=self.session, **kwargs)

    def indicator_attributes(self, **kwargs) -> IndicatorAttributes:
        """Return a instance of Indicator Attributes object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Group.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return IndicatorAttributes(session=self.session, **kwargs)

    def indicators(self, **kwargs) -> Indicators:
        """Return a instance of Indicators object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Indicator.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return Indicators(session=self.session, **kwargs)

    @cached_property
    def mitre_tags(self) -> MitreTags:
        """Mitre Tags"""
        mitre_tags = {}
        try:
            tags = Tags(session=self.session, params={'resultLimit': 1_000})
            tags.filter.technique_id(TqlOperator.NE, None)  # type: ignore
            for tag in tags:
                mitre_tags[str(tag.model.technique_id)] = tag.model.name
        except Exception as e:
            self.log.exception('Error downloading Mitre Tags')
            raise e
        return MitreTags(mitre_tags)

    def security_label(self, **kwargs) -> SecurityLabel:
        """Return a instance of Case Attributes object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            color (str, kwargs): Color of the security label.
            description (str, kwargs): Description of the security label.
            name (str, kwargs): Name of the security label.
            owner (str, kwargs): The name of the Owner of the Label.
        """
        return SecurityLabel(session=self.session, **kwargs)

    def victim(self, **kwargs) -> Victim:
        """Return a instance of Victim object.

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            assets (VictimAssets, kwargs): A list of victim assets corresponding to the Victim.
            associated_groups (Groups, kwargs): A list of groups that this indicator is associated
                with.
            attributes (VictimAttributes, kwargs): A list of Attributes corresponding to the
                Victim.
            description (str, kwargs): The indicator description text.
            name (str, kwargs): Name of the Victim.
            nationality (str, kwargs): Nationality of the Victim.
            org (str, kwargs): Org of the Victim.
            id (int, kwargs): The ID of the Victim.
            owner_name (str, kwargs): The name of the Organization, Community, or Source that the
                item belongs to.
            security_labels (SecurityLabels, kwargs): A list of Security Labels corresponding to the
                Intel item (NOTE: Setting this parameter will replace any existing tag(s) with the
                one(s) specified).
            suborg (str, kwargs): Suborg of the Victim.
            tags (Tags, kwargs): A list of Tags corresponding to the item (NOTE: Setting this
                parameter will replace any existing tag(s) with the one(s) specified)
            type (str, kwargs): The type for the Victim.
            work_location (str, kwargs): Work Location of the Victim.
        """

        return Victim(session=self.session, **kwargs)

    def victims(self, **kwargs) -> Victims:
        """Return a instance of Victims object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Indicator.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return Victims(session=self.session, **kwargs)

    def victim_asset(self, **kwargs) -> VictimAsset:
        """Return a instance of VictimAsset object."""

        return VictimAsset(session=self.session, **kwargs)

    def victim_assets(self, **kwargs) -> VictimAssets:
        """Return a instance of Victims object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Indicator.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return VictimAssets(session=self.session, **kwargs)

    def victim_attribute(self, **kwargs) -> VictimAttribute:
        """Return a instance of VictimAttribute object."""

        return VictimAttribute(session=self.session, **kwargs)

    def victim_attributes(self, **kwargs) -> VictimAttributes:
        """Return a instance of Victims object.

        .. code-block:: python
            :linenos:
            :lineno-start: 1

            # Example of params input
            {
                'result_limit': 100,  # How many results are retrieved.
                'result_start': 10,  # Starting point on retrieved results.
                'fields': ['caseId', 'summary']  # Additional fields returned on the results
            }

        Args:
            **kwargs: Additional keyword arguments.

        Keyword Args:
            initial_response (dict, optional): Initial data in Case Object for Indicator.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return VictimAttributes(session=self.session, **kwargs)
