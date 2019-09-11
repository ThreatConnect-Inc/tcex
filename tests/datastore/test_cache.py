# -*- coding: utf-8 -*-
"""Test the TcEx DataStore Module."""
import time


# pylint: disable=W0201
class TestCache:
    """Test the TcEx DataStore Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    @staticmethod
    def expired_data_callback(rid):  # pylint: disable=unused-argument
        """Return dummy data for cache callback."""
        return {'results': 'not-cached'}

    def test_cache_add(self, tcex, rid='cache-one', data=None, expire=10):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'one': 1}
        cache = tcex.cache('local', self.data_type, expire)
        results = cache.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_cache_delete(self, tcex, rid='cache-delete'):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        cache = tcex.cache('local', self.data_type, 10)

        # add entry to be deleted
        cache.add(rid=rid, data={'one': 1})

        # delete cache entry
        results = cache.delete(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_cache_get_cached(self, tcex, rid='cache-get'):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        cache = tcex.cache('local', self.data_type, 30)

        # add entry to get
        cache.add(rid=rid, data={'results': 'cached'})

        # get cache entry
        results = cache.get(rid=rid)
        assert results.get('results') == 'cached'

    def test_cache_get_expired(self, tcex, rid='cache-get-expire'):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        cache = tcex.cache('local', self.data_type, 10)

        # add entry to be retrieved
        results = cache.add(rid=rid, data={'one': 5}, ttl_seconds=5)

        time.sleep(10)
        results = cache.get(rid=rid, data_callback=self.expired_data_callback)
        print('results', results)
        assert results.get('results') == 'not-cached'

    def test_cache_update(self, tcex, rid='cache-one', data=None, expire=10):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'one': 1}
        cache = tcex.cache('local', self.data_type, expire)
        results = cache.update(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
