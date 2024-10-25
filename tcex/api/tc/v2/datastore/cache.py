"""TcEx Framework Module"""

# standard library
import logging
from collections.abc import Callable
from datetime import datetime, timedelta

# third-party
import arrow
from requests import Session

# first-party
from tcex.api.tc.v2.datastore.datastore import DataStore
from tcex.logger.trace_logger import TraceLogger
from tcex.util import Util

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class Cache:
    """TcEx Cache Class.

    Args:
        session: A requests.Session instance with auth configured for the ThreatConnect API.
        domain: A value of “system”, “organization”, or “local”.
        data_type: A free form type name for the data.
        ttl_seconds: Number of seconds the cache is valid.
        mapping: Elasticsearch mapping data.
    """

    def __init__(
        self,
        session: Session,
        domain: str,
        data_type: str,
        ttl_seconds: int | None = None,
        mapping: dict | None = None,
    ):
        """Initialize instance properties."""

        # properties
        self.ds = DataStore(session, domain, data_type, mapping)
        self.log = _logger
        self.ttl_seconds = ttl_seconds
        self.util = Util()

        # Warranty void if any of these are changed.  Don't touch.
        self._cache_data_key: str = 'cache-data'
        self._cache_date_key: str = 'cache-date'

    def add(self, rid: str, data: dict, raise_on_error: bool = True) -> dict | None:
        """Write cache data to the data store.

        **Example Response**

        .. code-block:: json

            {
              "_index": "$local.usr5_pytest",
              "_type": "pytest",
              "_id": "cache-one",
              "_version": 10,
              "result": "updated",
              "_shards": {
                  "total": 2,
                  "successful": 1,
                  "failed": 0
              },
              "_seq_no": 10,
              "_primary_term": 1
            }

        Args:
            rid: The record identifier.
            data: The record data.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The response dict
        """
        data = {
            self._cache_date_key: datetime.utcnow().isoformat(),
            self._cache_data_key: data,
        }
        return self.ds.post(rid, data, raise_on_error)

    def delete(self, rid: str, raise_on_error: bool = True) -> dict | None:
        """Write cache data to the data store.

        **Example Response**

        .. code-block:: json

            {
              "_index": "$local.usr5_pytest",
              "_type": "pytest",
              "_id": "cache-delete",
              "_version": 2,
              "result": "deleted",
              "_shards": {
                "total": 2,
                "successful": 1,
                "failed": 0
              },
              "_seq_no": 34,
              "_primary_term": 1
            }

        Args:
            rid: The record identifier.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The response dict.
        """
        return self.ds.delete(rid, raise_on_error)

    def get(
        self,
        rid: str,
        data_callback: Callable[[str], dict] | None = None,
        raise_on_error: bool = True,
    ) -> dict | None:
        """Get cached data from the data store.

        **Example Response**

        .. code-block:: json

            {
              "cache-date": "2020-07-31T11:44:53.851116",
              "cache-data": {
                "results": "cached"
              }
            }

        Args:
            rid: The record identifier.
            data_callback: A method that will return the data.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict: The cached data.
        """
        cache_data: dict | None = None
        ds_data: dict[str, bool | dict | str] | None = self.ds.get(rid, raise_on_error=False)

        if ds_data is None:
            # default the response when TC API doesn't return a value
            ds_data = {'found': False}

        if ds_data is not None:
            expired = False
            if ds_data.get('found') is True:
                cache_data = ds_data.get('_source') or {}  # type: ignore
                cache_date = cache_data[self._cache_date_key]  # type: ignore
                if self._is_cache_expired(cache_date):
                    cache_data = None
                    expired = True
                    self.log.debug(f'Cached data is expired for ({rid}).')

            if expired or ds_data.get('found') is False:
                # when cache is expired or does not exist use callback to get data if possible
                if callable(data_callback):
                    # cache_data = self._encode_data(data_callback(rid))
                    cache_data: dict | None = data_callback(rid)
                    self.log.debug(f'Using callback data for ({rid}).')
                    if cache_data:
                        cache_data = self.update(
                            rid, cache_data, raise_on_error
                        )  # update the cache data
            else:
                self.log.debug(f'Using cached data for ({rid}).')

        return cache_data

    def update(self, rid: str, data: dict, raise_on_error: bool = True) -> dict:
        """Write updated cache data to the DataStore.

        **Example Response**

        .. code-block:: json

            {
              "cache-date": "2020-07-31T11:44:53.851116",
              "cache-data": {
                "one": 1
              }
            }

        Args:
            rid: The record identifier.
            data: The record data.
            raise_on_error: If True and not r.ok this method will raise a RunTimeError.

        Returns:
            dict : The cached data.
        """
        cache_date = datetime.utcnow().isoformat()
        # cache_data = self._encode_data(data)
        data = {self._cache_date_key: cache_date, self._cache_data_key: data}
        self.ds.put(rid, data, raise_on_error)
        return data

    def _is_cache_expired(self, cached_date: str) -> bool:
        """Return True if the provided cache data is expired.

        Args:
            cached_date: The cache date value.

        Returns:
            bool: True if cache data is expired.
        """

        if self.ttl_seconds is None or self.ttl_seconds == 0:
            return True  # if ttl_is 0 or None, all cached data is always invalid.

        # convert the stored time expression to a datetime
        # object (support for different tcex version)
        cached_datetime = self.util.any_to_datetime(cached_date).datetime

        # calculate the cache expiration time by adding the ttl seconds to the cached time
        cache_expires = cached_datetime + timedelta(seconds=self.ttl_seconds)

        # if cache expires is less than "now" then return True/expired
        return cache_expires < arrow.get(datetime.utcnow())
