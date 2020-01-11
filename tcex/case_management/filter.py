# -*- coding: utf-8 -*-
"""ThreatConnect Case Management Filter Module"""


class Filter:
    """Filter Base Class

    Args:
        tql (TQL): Instance of TQL Class.
    """

    def __init__(self, api_endpoint, tcex, tql):
        """Initialize Class properties"""
        self._api_endpoint = api_endpoint.value
        self._tcex = tcex
        self._tql = tql
        self._tql_data = None

    @property
    def implemented_keywords(self):
        """Return implemented TQL keywords."""
        keywords = []
        for prop in dir(self):
            if prop.startswith('_') or prop in ['tql']:
                continue
            # remove underscore from method name to match keyword
            keywords.append(prop.replace('_', ''))

        return keywords

    @property
    def descriptions(self):
        """Return supported TQL descriptions."""
        return [td.get('description') for td in self.tql_data]

    @property
    def keyword_map(self):
        """Return keyword to method name map."""

        return {
            'active': 'active',
            'assignedgroupid': 'assigned_group_id',
            'assigneduserid': 'assigned_user_id',
            'caseid': 'case_id',
            'caseseverity': 'case_severity',
            'completeddate': 'completed_date',
            'configartifact': 'config_artifact',
            'configplaybook': 'config_playbook',
            'configtask': 'config_task',
            'dateadded': 'date_added',
            'deleted': 'deleted',
            'deletedreason': 'deleted_reason',
            'description': 'description',
            'duedate': 'due_date',
            'eventdate': 'event_date',
            'hascase': 'has_case',
            'id': 'id',
            'link': 'link',
            'linktext': 'link_text',
            'name': 'name',
            'owner': 'owner',
            'ownername': 'owner_name',
            'organizationid': 'organization_id',
            'status': 'status',
            'summary': 'summary',
            'systemgenerated': 'system_generated',
            'targetid': 'target_id',
            'targettype': 'target_type',
            'version': 'version',
            'username': 'username',
            'xid': 'xid',
        }

    @property
    def keywords(self):
        """Return supported TQL keywords."""
        return [td.get('keyword') for td in self.tql_data]

    @property
    def names(self):
        """Return supported TQL names."""
        return [td.get('name') for td in self.tql_data]

    @property
    def tql_data(self):
        """Return TQL data keywords."""
        if self._tql_data is None:
            r = self._tcex.session.options(f'{self._api_endpoint}/tql', params={})
            if r.ok:
                self._tql_data = r.json()['data']

        return self._tql_data

    @property
    def types(self):
        """Return supported TQL types."""
        return [td.get('type') for td in self.tql_data]

    def tql(self, tql):
        """Filter objects based on TQL expression.

        Args:
            tql (str): The raw TQL string for the filter.
        """
        self._tql.set_raw_tql(tql)
