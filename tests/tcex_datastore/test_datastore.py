# -*- coding: utf-8 -*-
"""Test the TcEx DataStore Module."""

from ..tcex_init import tcex


# pylint: disable=W0201
class TestDataStore:
    """Test the TcEx DataStore Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    def test_data_store_local_index(self):
        """Test data store add."""
        tcex.datastore('local', self.data_type)

    def test_data_store_local_add(self, rid='one', data=None):
        """Test data store add."""
        if data is None:
            data = {'one': 1}
        ds = tcex.datastore('local', self.data_type)
        results = ds.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_delete(self, rid='three'):
        """Test data store add."""
        # add
        self.test_data_store_local_add(rid, {'three': 3})

        # delete
        ds = tcex.datastore('local', self.data_type)
        results = ds.delete(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_data_store_local_get(self, rid='two', data=None):
        """Test data store add."""
        if data is None:
            data = {'two': 2}
        self.test_data_store_local_add(rid, data)

        ds = tcex.datastore('local', self.data_type)
        results = ds.get(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_source').get('two') == 2
        assert results.get('found') is True

        # delete
        self.test_data_store_local_delete(rid)

    def test_data_store_organization_add(self, rid='one', data=None):
        """Test data store add."""
        if data is None:
            data = {'one': 1}
        ds = tcex.datastore('organization', self.data_type)
        results = ds.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_data_store_organization_delete(self, rid='three'):
        """Test data store add."""
        # add
        self.test_data_store_organization_add(rid, {'three': 3})

        # delete
        ds = tcex.datastore('organization', self.data_type)
        results = ds.delete(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_data_store_orgnaization_get(self, rid='two', data=None):
        """Test data store add."""
        if data is None:
            data = {'two': 2}
        self.test_data_store_organization_add(rid, data)

        ds = tcex.datastore('organization', self.data_type)
        results = ds.get(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_source').get('two') == 2
        assert results.get('found') is True

        # delete
        self.test_data_store_organization_delete(rid)
