# -*- coding: utf-8 -*-
"""TcEx Framework Module for working with Datastore in the ThreatConnect Platform."""
# import base64
from datetime import datetime, timedelta
from tcex import TcEx


class Cache:
    """TcEx Cache Class."""

    def __init__(self, tcex: TcEx, domain, data_type, ttl_seconds=None, mapping=None):
        """Initialize class properties.

        Args:
            tcex (object): An instance of TcEx.
            domain (str): A value of “system”, “organization”, or “local”.
            data_type (str): A free form type name for the data.
            ttl_seconds (int, optional): Defaults to None. Number of seconds the cache is valid.
            mapping (dict, optional): Defaults to None. ElasticSearch mappings data.
        """
        self.tcex: TcEx = tcex

        # properties
        self.ttl_seconds = ttl_seconds
        self.ds: TcEx.datastore = self.tcex.datastore(domain, data_type, mapping)

        # Warranty void if any of these are changed.  Don't touch.
        self._cache_data_key = 'cache-data'
        self._cache_date_key = 'cache-date'

    @staticmethod
    def _dt_to_epoch(dt):
        """Convert datetime to epoch seconds."""
        try:
            epoch = dt.timestamp()
        except AttributeError:  # py2
            epoch = (dt - datetime(1970, 1, 1)).total_seconds()
        return epoch

    def add(self, rid, data, raise_on_error=True):
        """Write cache data to the data store.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.
        Returns:
            object : Python request response.
        """
        data = {self._cache_date_key: datetime.utcnow().isoformat(), self._cache_data_key: data}
        return self.ds.post(rid, data, raise_on_error)

    def delete(self, rid, raise_on_error=True):
        """Write cache data to the data store.

        Args:
            rid (str): The record identifier.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        return self.ds.delete(rid, raise_on_error)

    def get(self, rid, data_callback=None, raise_on_error=True):
        """Get cached data from the data store.

        Args:
            rid (str): The record identifier.
            data_callback (callable): A method that will return the data.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.
        Returns:
            object : Python request response.
        """
        cache_data = None
        ds_data = self.ds.get(rid, raise_on_error=False)
        if ds_data is None:
            ds_data = {'found': False}
        if ds_data is not None:
            expired = False
            if ds_data.get('found') is True:
                cache_data = ds_data.get('_source', {})
                cache_date = cache_data.get(self._cache_date_key)
                if self._is_cache_expired(cache_date):
                    cache_data = None
                    expired = True
                    self.tcex.log.debug(f'Cached data is expired for ({rid}).')

            if expired or ds_data.get('found') is False:
                # when cache is expired or does not exist use callback to get data if possible
                if callable(data_callback):
                    # cache_data = self._encode_data(data_callback(rid))
                    cache_data = data_callback(rid)
                    self.tcex.log.debug(f'Using callback data for ({rid}).')
                    if cache_data:
                        cache_data = self.update(
                            rid, cache_data, raise_on_error
                        )  # update the cache data
            else:
                self.tcex.log.debug(f'Using cached data for ({rid}).')

        return cache_data

    def update(self, rid, data, raise_on_error=True):
        """Write updated cache data to the DataStore.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        cache_date = datetime.utcnow().isoformat()
        # cache_data = self._encode_data(data)
        data = {self._cache_date_key: cache_date, self._cache_data_key: data}
        self.ds.put(rid, data, raise_on_error)
        return data

    def _is_cache_expired(self, cached_date):
        cached_datetime = self.tcex.utils.datetime.any_to_datetime(cached_date)
        cache_expires = (cached_datetime + timedelta(seconds=self.ttl_seconds)).timestamp()
        return cache_expires < datetime.utcnow().timestamp()
