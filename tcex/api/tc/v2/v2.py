"""Case Management"""
# standard library
from typing import TYPE_CHECKING, Optional

# first-party
from tcex.api.tc.v2.datastore.cache import Cache
from tcex.api.tc.v2.datastore.datastore import DataStore
from tcex.api.tc.v2.metrics.metrics import Metrics
from tcex.api.tc.v2.notifications.notifications import Notifications

if TYPE_CHECKING:
    # third-party
    from requests import Session


class V2:
    """Case Management

    Args:
        session_tc: An configured instance of request.Session with TC API Auth.
    """

    def __init__(self, session_tc: 'Session') -> None:
        """Initialize Class properties."""
        self.session_tc = session_tc

    def cache(
        self,
        domain: str,
        data_type: str,
        ttl_seconds: Optional[int] = None,
        mapping: Optional[dict] = None,
    ) -> Cache:
        """Get instance of the Cache module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            ttl_seconds: The number of seconds the cache is valid.
            mapping: Advanced - The datastore mapping if required.
        """
        return Cache(self.session_tc, domain, data_type, ttl_seconds, mapping)

    def datastore(self, domain: str, data_type: str, mapping: Optional[dict] = None) -> DataStore:
        """Return Datastore Module.

        Args:
            domain: The domain can be either "system", "organization", or "local". When using
                "organization" the data store can be accessed by any Application in the entire org,
                while "local" access is restricted to the App writing the data. The "system" option
                should not be used in almost all cases.
            data_type: The data type descriptor (e.g., tc:whois:cache).
            mapping: ElasticSearch mappings data.
        """
        return DataStore(
            session_tc=self.session_tc, domain=domain, data_type=data_type, mapping=mapping
        )

    def metric(
        self,
        name: str,
        description: str,
        data_type: str,
        interval: str,
        keyed: Optional[bool] = False,
    ) -> Metrics:
        """Get instance of the Metrics module.

        Args:
            name: The name for the metric.
            description: The description of the metric.
            data_type: The type of metric: Sum, Count, Min, Max, First, Last, and Average.
            interval: The metric interval: Hourly, Daily, Weekly, Monthly, and Yearly.
            keyed: Indicates whether the data will have a keyed value.
        """
        return Metrics(
            session_tc=self.session_tc,
            name=name,
            description=description,
            data_type=data_type,
            interval=interval,
            keyed=keyed,
        )

    def notification(self) -> Notifications:
        """Get instance of the Notification module."""
        return Notifications(self.session_tc)
