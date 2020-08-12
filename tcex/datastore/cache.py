# -*- coding: utf-8 -*-
"""TcEx Framework Module for working with Cache in the ThreatConnect Platform."""
# standard library
from datetime import datetime, timedelta
from typing import Callable, Optional


class Cache:
    """TcEx Cache Class.

    Args:
        tcex (TcEx): An instance of TcEx.
        domain (str): A value of "organization" or "local".
        data_type (str): A free form type name for the data.
        ttl_seconds (Optional[int] = None): Number of seconds the cache is valid.
        mapping (Optional[dict] = None): ElasticSearch mappings data.
    """

    def __init__(
        self,
        tcex: object,
        domain: str,
        data_type: str,
        ttl_seconds: Optional[int] = None,
        mapping: Optional[dict] = None,
    ):
        """Initialize class properties."""
        self.tcex: object = tcex

        # properties
        self.ttl_seconds: Optional[int] = ttl_seconds
        self.ds: 'tcex.datastore' = self.tcex.datastore(domain, data_type, mapping)

        # Warranty void if any of these are changed.  Don't touch.
        self._cache_data_key: str = 'cache-data'
        self._cache_date_key: str = 'cache-date'

    def add(self, rid: str, data: dict, raise_on_error: Optional[bool] = True) -> dict:
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
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

        Returns:
            dict : The response dict
        """
        data: dict = {
            self._cache_date_key: datetime.utcnow().isoformat(),
            self._cache_data_key: data,
        }
        return self.ds.post(rid, data, raise_on_error)

    def delete(self, rid: str, raise_on_error: Optional[bool] = True) -> dict:
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
            rid (str): The record identifier.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                 method will raise a RunTimeError.

        Returns:
            dict : The response dict.
        """
        return self.ds.delete(rid, raise_on_error)

    def get(
        self,
        rid: str,
        data_callback: Optional[Callable[[str], dict]] = None,
        raise_on_error: Optional[bool] = True,
    ) -> dict:
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
            rid (str): The record identifier.
            data_callback (Optional[Callable] = None): A method that will return the data.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
                method will raise a RunTimeError.

        Returns:
            dict : The cached data.
        """
        cache_data = None
        ds_data: dict = self.ds.get(rid, raise_on_error=False)

        if ds_data is None:
            # default the response when TC API doesn't return a value
            ds_data = {'found': False}

        if ds_data is not None:
            expired = False
            if ds_data.get('found') is True:
                cache_data: dict = ds_data.get('_source', {})
                cache_date: str = cache_data.get(self._cache_date_key)
                if self._is_cache_expired(cache_date):
                    cache_data = None
                    expired = True
                    self.tcex.log.debug(f'Cached data is expired for ({rid}).')

            if expired or ds_data.get('found') is False:
                # when cache is expired or does not exist use callback to get data if possible
                if callable(data_callback):
                    # cache_data = self._encode_data(data_callback(rid))
                    cache_data: Optional[dict] = data_callback(rid)
                    self.tcex.log.debug(f'Using callback data for ({rid}).')
                    if cache_data:
                        cache_data = self.update(
                            rid, cache_data, raise_on_error
                        )  # update the cache data
            else:
                self.tcex.log.debug(f'Using cached data for ({rid}).')

        return cache_data

    def update(self, rid: str, data: dict, raise_on_error: Optional[bool] = True) -> dict:
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
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (Optional[bool] = True): If True and not r.ok this
               method will raise a RunTimeError.

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
            cached_date (str): The cache date value.

        Returns:
            bool: True if cache data is expired.
        """

        if self.ttl_seconds is None or self.ttl_seconds == 0:
            return True  # if ttl_is 0 or None, all cached data is always invalid.

        cached_datetime = self.tcex.utils.datetime.any_to_datetime(cached_date)
        cache_expires = (cached_datetime + timedelta(seconds=self.ttl_seconds)).timestamp()
        return cache_expires < datetime.utcnow().timestamp()
