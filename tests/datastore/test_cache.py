# -*- coding: utf-8 -*-
"""Test the TcEx DataStore Module."""
import time

from ..tcex_init import tcex


# pylint: disable=W0201
class TestDataStore:
    """Test the TcEx DataStore Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    def test_cache_add(self, rid='cache-one', data=None, expire=1):
        """Test data store add."""
        if data is None:
            data = {'one': 1}
        cache = tcex.cache('local', self.data_type, expire)
        results = cache.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_cache_delete(self, rid='cache-delete'):
        """Test data store add."""
        self.test_cache_add(rid, {'delete': 'delete'})

        cache = tcex.cache('local', self.data_type, 1)
        results = cache.delete(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_cache_get(self, rid='cache-get'):
        """Test data store add."""
        self.test_cache_add(rid, {'get': 'get'})

        cache = tcex.cache('local', self.data_type, 1)
        results = cache.get(rid=rid)
        assert results.get('get') == 'get'

    @staticmethod
    def expired_data_callback(rid):
        """Return dummy data for cache callback."""
        return {'dummy-data': rid}

    def test_cache_get_expired(self, rid='cache-get-expire'):
        """Test data store add."""
        self.test_cache_add(rid, {'get': 'get'}, expire=1)

        time.sleep(61)
        cache = tcex.cache('local', self.data_type, 1)
        results = cache.get(rid=rid, data_callback=self.expired_data_callback)
        assert results.get('dummy-data') == 'cache-get-expire'

    def test_cache_update(self, rid='cache-one', data=None, expire=1):
        """Test data store add."""
        if data is None:
            data = {'one': 1}
        cache = tcex.cache('local', self.data_type, expire)
        results = cache.update(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
