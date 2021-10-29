"""Threat Intelligence"""
# third-party
from requests import Session

# first-party
from tcex.api.tc.v3.groups.group import Group, Groups
from tcex.api.tc.v3.indicators.indicator import Indicator, Indicators


class ThreatIntelligence:
    """Threat Intelligence

    Args:
        session: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session: Session) -> None:
        """Initialize Class properties."""
        self.session = session

    def group(self, **kwargs) -> 'Group':
        """Return a instance of Group object.

        Args:
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

    def groups(self, **kwargs) -> 'Groups':
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
            initial_response (dict, optional): Initial data in Case Object for Group.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return Groups(session=self.session, **kwargs)

    @property
    def indicator(self, **kwargs) -> 'Indicator':
        """Return a instance of Group object.

        Args:
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

    def indicators(self, **kwargs) -> 'Indicators':
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
            initial_response (dict, optional): Initial data in Case Object for Indicator.
            tql_filters (list, optional): A list of TQL filters.
            params (dict, optional): A dict of query params for the request.
        """
        return Indicators(session=self.session, **kwargs)
