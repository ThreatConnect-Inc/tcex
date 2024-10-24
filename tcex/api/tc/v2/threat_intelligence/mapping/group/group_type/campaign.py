"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group import Group

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class Campaign(Group):
    """Unique API calls for Campaign API Endpoints

    Args:
        ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
        name (str, kwargs): [Required for Create] The name for this Group.
        owner (str, kwargs): The name for this Group. Default to default Org when not provided
        first_seen (str, kwargs): The first seen datetime expression for this Group.
    """

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties."""
        super().__init__(
            ti, sub_type='Campaign', api_entity='campaign', api_branch='campaigns', **kwargs
        )

    def first_seen(self, first_seen):
        """Update the campaign with the new first_seen date.

        Args:
            first_seen (str): The first_seen date. Converted to %Y-%m-%dT%H:%M:%SZ date format

        Returns:
            requests.Response: The response from the API call.
        """
        if not self.can_update():
            self._handle_error(910, [self.type])

        first_seen = self.util.any_to_datetime(first_seen).strftime('%Y-%m-%dT%H:%M:%SZ')
        self._data['firstSeen'] = first_seen
        request = {'firstSeen': first_seen}
        return self.tc_requests.update(self.api_type, self.api_branch, self.unique_id, request)
