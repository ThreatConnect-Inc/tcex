# -*- coding: utf-8 -*-
"""Test the TcEx DataStore Module."""
# standard library
import time


class TestCache:
    """Test the TcEx DataStore Module."""

    data_type = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    @staticmethod
    def expired_data_callback(rid):  # pylint: disable=unused-argument
        """Return dummy data for cache callback."""
        return {'results': 'not-cached'}

    def test_cache_add(self, tcex):
        """Test adding data to a cache

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        data = {'one': 1}
        expire = 10
        rid = 'cache-one'

        cache = tcex.cache('local', self.data_type, expire)
        results = cache.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_cache_delete(self, tcex):
        """Test deleting data from a cache

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        rid = 'cache-delete'

        # get cache instance
        cache = tcex.cache('local', self.data_type, 10)

        # add entry to be deleted
        cache.add(rid=rid, data={'one': 1})

        # delete cache entry
        results = cache.delete(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_cache_get_cached(self, tcex):
        """Test getting data from a cache

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        rid = 'cache-get'

        # get cache instance
        cache = tcex.cache('local', self.data_type, 300)

        # add entry to get
        cache.add(rid=rid, data={'results': 'cached'})

        # get cache entry
        results = cache.get(rid=rid)
        assert results.get('cache-data', {}).get('results') == 'cached'

    def test_cache_get_expired(self, tcex):
        """Test ttl on a cache item.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        rid = 'cache-get-expire'

        # get cache instance
        cache = tcex.cache('local', self.data_type, 1)

        # add entry to be retrieved
        results = cache.add(rid=rid, data={'one': 5})

        time.sleep(3)
        results = cache.get(rid=rid, data_callback=self.expired_data_callback)
        assert results.get('cache-data') == self.expired_data_callback(rid)

    def test_cache_update(self, tcex):
        """Test update on cache data

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        data = {'one': 1}
        expire = 10
        rid = 'cache-get'

        # get cache instance
        cache = tcex.cache('local', self.data_type, expire)

        results = cache.update(rid=rid, data=data)
        assert results.get('cache-data') == data
