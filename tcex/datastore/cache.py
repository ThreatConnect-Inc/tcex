# -*- coding: utf-8 -*-
"""TcEx Framework Module for working with Datastore in the ThreatConnect Platform."""
# import base64
import time
from datetime import datetime, timedelta


class Cache(object):
    """TcEx Cache Class."""

    def __init__(self, tcex, domain, data_type, ttl_seconds=None, mapping=None):
        """Initialize class properties.

        Args:
            tcex (object): An instance of TcEx.
            domain (str): A value of “system”, “organization”, or “local”.
            data_type (str): A free form type name for the data.
            seconds (int, optional): Defaults to None. Number of seconds the cache is valid.
            mapping (dict, optional): Defaults to None. Elasticsearch mappings data.
        """
        self.tcex = tcex

        # properties
        self.ttl_seconds = ttl_seconds
        self.ds = self.tcex.datastore(domain, data_type, mapping)

    def _cache_date(self, ttl_seconds):
        """Return the cache date."""
        cache_date = None
        ttl_seconds = ttl_seconds or self.ttl_seconds
        if ttl_seconds:
            cache_date = self._dt_to_epoch(datetime.utcnow() + timedelta(seconds=int(ttl_seconds)))
        return cache_date

    # def _decode_data(self, data):
    #     """Return the cache data encoded."""
    #     if data is not None:
    #         data = base64.b64decode(data)
    #         try:
    #             data = data.decode('utf-8')
    #         except UnicodeDecodeError:
    #             data = data.decode('latin-1')
    #     return data

    # def _encode_data(self, data):
    #     """Return the cache data encoded."""
    #     if data is not None:
    #         try:
    #             # py2
    #             data = base64.b64encode(bytes(data)).decode('utf-8')
    #         except TypeError:
    #             # py3
    #             data = base64.b64encode(bytes(data, 'utf-8')).decode('utf-8')
    #     return data

    @staticmethod
    def _dt_to_epoch(dt):
        """Convert datetime to epoch seconds."""
        try:
            epoch = dt.timestamp()
        except AttributeError:  # py2
            epoch = (dt - datetime(1970, 1, 1)).total_seconds()
        return epoch

    def add(self, rid, data, ttl_seconds=None, raise_on_error=True):
        """Write cache data to the data store.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            ttl_seconds (int, optional): Defaults to None. Number of seconds the cache is valid.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        cache_date = self._cache_date(ttl_seconds)
        # cache_data = self._encode_data(data)
        data = {'cache-date': cache_date, 'cache-data': data}
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
        if ds_data is not None:
            expired = False
            if ds_data.get('found') is True:
                cache_date = ds_data.get('_source', {}).get('cache-date')
                cache_data = ds_data.get('_source', {}).get('cache-data')
                if cache_date is not None and int(time.time()) > int(cache_date):
                    cache_data = None
                    expired = True
                    self.tcex.log.debug('Cached data is expired for ({}).'.format(rid))

            if expired or ds_data.get('found') is False:
                # when cache is expired or does not exist use callback to get data if possible
                if callable(data_callback):
                    # cache_data = self._encode_data(data_callback(rid))
                    cache_data = data_callback(rid)
                    self.tcex.log.debug('Using callback data for ({}).'.format(rid))
                    if cache_data:
                        self.update(rid, cache_data, raise_on_error)  # update the cache data
            else:
                self.tcex.log.debug('Using cached data for ({}).'.format(rid))
        return cache_data

    def update(self, rid, data, ttl_seconds=None, raise_on_error=True):
        """Write updated cache data to the DataStore.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            ttl_seconds (int, optional): Defaults to None. Number of seconds the cache is valid.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        cache_date = self._cache_date(ttl_seconds)
        # cache_data = self._encode_data(data)
        data = {'cache-date': cache_date, 'cache-data': data}
        return self.ds.put(rid, data, raise_on_error)
