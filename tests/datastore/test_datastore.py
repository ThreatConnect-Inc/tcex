# -*- coding: utf-8 -*-
"""Test the TcEx DataStore Module."""
import json
import uuid


class MockPost:
    """Mock tcex session.get() method."""

    def __init__(self, data, ok=True):
        """Initialize class properties."""
        self.data = data
        self.ok = ok

    @property
    def headers(self):
        """Mock headers property"""
        return {'content-type': 'application/json'}

    def json(self):
        """Mock json method"""
        return self.data

    @property
    def ok(self):
        """Mock ok property"""
        return self.ok

    @property
    def reason(self):
        """Mock reason property"""
        return 'reason'

    @property
    def status_code(self):
        """Mock status_code property"""
        return 500

    @property
    def text(self):
        """Mock text property"""
        return json.dumps(self.data)


# pylint: disable=W0201
class TestDataStore:
    """Test the TcEx DataStore Module."""

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    @staticmethod
    def test_create_index_fail_test(monkeypatch, tcex):
        """Test load_secure_params method."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        post_orig = tcex.session.post

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        monkeypatch.setattr(tcex.session, 'post', mp_post)

        # create index
        key = str(uuid.uuid4())
        try:
            tcex.datastore('local', key)
            assert False, 'Failed to catch error on ok=False'
        except RuntimeError:
            assert True

        # reset monkeypatched tcex.session.get()
        tcex.session.post = post_orig

    def test_data_store_local_index(self, tcex):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        tcex.datastore('local', self.data_type)

    @staticmethod
    def test_data_store_local_new_index(tcex, rid='one', data=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        key = str(uuid.uuid4())
        if data is None:
            data = {'one': 1}
        ds = tcex.datastore('local', key)
        results = ds.add(rid=rid, data=data)
        assert results.get('_type') == key
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_add(self, tcex, rid='one', data=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'one': 1}
        ds = tcex.datastore('local', self.data_type)
        results = ds.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_add_no_rid(self, tcex, rid=None, data=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'one': 1}
        ds = tcex.datastore('local', self.data_type)
        results = ds.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_add_fail(self, monkeypatch, tcex, rid=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        post_orig = tcex.session.post

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session, 'post', mp_post)
        try:
            ds.add(rid=rid, data=None)
            assert False
        except RuntimeError:
            assert True

        # reset monkeypatched tcex.session.get()
        tcex.session.post = post_orig

    def test_data_store_local_delete(self, tcex, rid='three'):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        ds = tcex.datastore('local', self.data_type)

        # add entry to be deleted
        ds.add(rid, {'delete': 'delete'})

        # delete
        results = ds.delete(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_data_store_local_delete_fail(self, monkeypatch, tcex, rid='fail-test'):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        post_orig = tcex.session.post

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session, 'post', mp_post)
        try:
            ds.delete(rid=rid)
            assert False
        except RuntimeError:
            assert True

        # reset monkeypatched tcex.session.get()
        tcex.session.post = post_orig

    def test_data_store_local_get(self, tcex, rid='two', data=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'two': 2}
        ds = tcex.datastore('local', self.data_type)

        # add entry to be deleted
        ds.add(rid, data)

        results = ds.get(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_source').get('two') == 2
        assert results.get('found') is True

        # delete
        ds.delete(rid)

    def test_data_store_local_get_no_rid(self, tcex):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        ds = tcex.datastore('local', self.data_type)
        results = ds.get()
        assert results.get('hits') is not None

    def test_data_store_local_get_fail(self, monkeypatch, tcex):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        post_orig = tcex.session.post

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session, 'post', mp_post)
        try:
            ds.get()
            assert False
        except RuntimeError:
            assert True

        # reset monkeypatched tcex.session.get()
        tcex.session.post = post_orig

    def test_data_store_organization_add(self, tcex, rid='one', data=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'one': 1}
        ds = tcex.datastore('organization', self.data_type)

        results = ds.add(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_data_store_organization_delete(self, tcex, rid='three'):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        ds = tcex.datastore('organization', self.data_type)

        # add entry to be deleted
        ds.add(rid, {'three': 3})

        # delete
        results = ds.delete(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_data_store_organization_get(self, tcex, rid='two', data=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'two': 2}
        ds = tcex.datastore('organization', self.data_type)

        # add entry to get
        ds.add(rid, data)

        results = ds.get(rid=rid)
        assert results.get('_type') == self.data_type
        assert results.get('_source').get('two') == 2
        assert results.get('found') is True

        # delete
        ds.delete(rid)

    def test_data_store_local_put(self, tcex, rid='one', data=None):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        if data is None:
            data = {'one': 1}
        ds = tcex.datastore('local', self.data_type)

        # add entry to update
        ds.add(rid, {'one': 2})

        results = ds.put(rid=rid, data=data)
        assert results.get('_type') == self.data_type
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_put_fail(self, monkeypatch, tcex):
        """Test data store add."""
        args = tcex.args  # noqa: F841; pylint: disable=unused-variable
        post_orig = tcex.session.post

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session, 'post', mp_post)
        try:
            ds.update(rid=None, data=None)
            assert False
        except RuntimeError:
            assert True

        # reset monkeypatched tcex.session.get()
        tcex.session.post = post_orig
