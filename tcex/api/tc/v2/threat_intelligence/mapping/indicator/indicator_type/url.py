"""TcEx Framework Module"""

# standard library
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.indicator.indicator import Indicator

if TYPE_CHECKING:
    # first-party
    from tcex.api.tc.v2.threat_intelligence.threat_intelligence import ThreatIntelligence


class URL(Indicator):
    """Unique API calls for URL API Endpoints"""

    def __init__(self, ti: 'ThreatIntelligence', **kwargs):
        """Initialize instance properties.

        Args:
            ti (ThreatIntelligence): An instance of the ThreatIntelligence Class.
            **kwargs: Additional keyword arguments.

        Keyword Args:
            text (str, kwargs): [Required for Create] The URL value for this Indicator.
            active (bool, kwargs): If False the indicator is marked "inactive" in TC.
            confidence (str, kwargs): The threat confidence for this Indicator.
            date_added (str, kwargs): [Read-Only] The date timestamp the Indicator was created.
            last_modified (str, kwargs): [Read-Only] The date timestamp the Indicator was last
                modified.
            private_flag (bool, kwargs): If True the indicator is marked as private in TC.
            rating (str, kwargs): The threat rating for this Indicator.
            xid (str, kwargs): The external id for this Indicator.
        """
        super().__init__(ti, sub_type='URL', api_entity='url', api_branch='urls', **kwargs)
        self.unique_id = kwargs.get('unique_id', kwargs.get('text'))
        self.data['text'] = self.unique_id
        if self.unique_id:
            self.unique_id = quote_plus(self.fully_decode_uri(self.unique_id))

    def can_create(self):
        """Return True if address can be created.

        If the text has been provided returns that the URL can be created, otherwise
        returns that the URL cannot be created.
        """
        return self.data.get('text') is not None

    def _set_unique_id(self, json_response):
        """Set the unique_id provided a json response."""
        self.unique_id = quote_plus(self.fully_decode_uri(json_response.get('text', '')))
