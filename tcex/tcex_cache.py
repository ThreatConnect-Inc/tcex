# -*- coding: utf-8 -*-
"""TcEx Framework Module for working with Datastore in the ThreatConnect Platform."""
from datetime import datetime, timedelta


class TcExCache(object):
    """TcEx Cache Class."""

    def __init__(self, tcex, domain, data_type, ttl_minutes=None, mapping=None):
        """Initialize class properties.

        Args:
            tcex (object): An instance of TcEx.
            domain (): [description]
            data_type ([type]): [description]
            ttl_minutes (int, optional): Defaults to None. Number of minutes the cache is valid.
            mapping ([type], optional): Defaults to None. [description]
        """
        self.tcex = tcex

        # properties
        self.ttl = None
        if ttl_minutes is not None:
            self.ttl = self._dt_to_epoch(datetime.now() - timedelta(minutes=int(ttl_minutes)))
        self.ds = self.tcex.datastore(domain, data_type, mapping)

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
        cache_data = {'cache-date': self._dt_to_epoch(datetime.now()), 'cache-data': data}
        return self.ds.post(rid, cache_data, raise_on_error)

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
        cached_data = None
        ds_data = self.ds.get(rid, raise_on_error=False)
        if ds_data is not None:
            expired = True
            if ds_data.get('found') is True:
                if self.ttl < int(ds_data.get('_source', {}).get('cache-date', 0)):
                    cached_data = ds_data.get('_source', {}).get('cache-data')
                    expired = False
                    self.tcex.log.debug('Using cached data for ({}).'.format(rid))
                else:
                    self.tcex.log.debug('Cached data is expired for ({}).'.format(rid))

            if expired or ds_data.get('found') is False:
                # when cache is expired or does not exist use callback to get data if possible
                if callable(data_callback):
                    cached_data = data_callback(rid)
                    self.tcex.log.debug('Using callback data for ({}).'.format(rid))
                    if cached_data:
                        self.update(rid, cached_data, raise_on_error)  # update the cache data
        return cached_data

    def update(self, rid, data, raise_on_error=True):
        """Write updated cache data to the DataStore.

        Args:
            rid (str): The record identifier.
            data (dict): The record data.
            raise_on_error (bool): If True and not r.ok this method will raise a RunTimeError.

        Returns:
            object : Python request response.
        """
        cache_data = {'cache-date': self._dt_to_epoch(datetime.now()), 'cache-data': data}
        return self.ds.put(rid, cache_data, raise_on_error)
