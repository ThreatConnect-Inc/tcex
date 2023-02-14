"""Test the TcEx DataStore Module."""
# standard library
import json
import uuid
from typing import TYPE_CHECKING

# third-party
import pytest

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


class MockPost:
    """Mock tcex session.get() method."""

    def __init__(self, data, ok=True):
        """Initialize class properties."""
        self.data = data
        self._ok = ok

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
        return self._ok

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


class TestDataStore:
    """Test the TcEx DataStore Module."""

    data_type = None

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    @staticmethod
    def test_create_index_fail_test(tcex: 'TcEx', monkeypatch):
        """Test failure to create an index.

        Args:
            tcex (fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        monkeypatch.setattr(tcex.session_tc, 'post', mp_post)

        # create index
        key = str(uuid.uuid4())
        try:
            tcex.v2.datastore('local', key)
            assert False, 'Failed to catch error on ok=False'
        except RuntimeError:
            assert True

    def test_data_store_local_index(self, tcex: 'TcEx'):
        """Test creating a local datastore index

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        tcex.v2.datastore('local', self.data_type)

    @staticmethod
    def test_data_store_local_new_index(tcex: 'TcEx'):
        """Test creating a local datastore index

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        data = {'one': 1}
        key = str(uuid.uuid4())
        rid = 'one'

        ds = tcex.v2.datastore('local', key)

        results = ds.add(rid=rid, data=data)
        assert results.get('_id') == rid
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_add(self, tcex: 'TcEx'):
        """Test local datastore add

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        data = {'one': 1}
        rid = 'one'

        ds = tcex.v2.datastore('local', self.data_type)

        results = ds.add(rid=rid, data=data)
        assert results.get('_id') == rid
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_add_fail(self, tcex: 'TcEx', monkeypatch):
        """Test failure of data store add

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """
        rid = None

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.v2.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session_tc, 'post', mp_post)
        try:
            ds.add(rid=rid, data=None)
            assert False
        except RuntimeError:
            assert True

    def test_data_store_local_delete(self, tcex: 'TcEx'):
        """Test local datastore delete

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        rid = 'three'

        ds = tcex.v2.datastore('local', self.data_type)

        # add entry to be deleted
        ds.add(rid, {'delete': 'delete'})

        # delete
        results = ds.delete(rid=rid)
        assert results.get('_id') == rid
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_data_store_local_delete_fail(self, tcex: 'TcEx', monkeypatch):
        """Test failure of data store local delete

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """
        rid = 'fail-test'

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.v2.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session_tc, 'post', mp_post)
        try:
            ds.delete(rid=rid)
            assert False
        except RuntimeError:
            assert True

    def test_data_store_local_get(self, tcex: 'TcEx'):
        """Test local datastore get

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        data = {'two': 2}
        rid = 'two'

        ds = tcex.v2.datastore('local', self.data_type)

        # add entry to be deleted
        ds.add(rid, data)

        results = ds.get(rid=rid)
        assert results.get('_id') == rid
        assert results.get('_source').get('two') == 2
        assert results.get('found') is True

        # delete
        ds.delete(rid)

    def test_data_store_local_get_no_rid(self, tcex: 'TcEx'):
        """Test local datastore get no reid

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        ds = tcex.v2.datastore('local', self.data_type)

        results = ds.get()
        assert results.get('hits') is not None

    def test_data_store_local_get_fail(self, tcex: 'TcEx', monkeypatch):
        """Test failure of data store local get

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.v2.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session_tc, 'post', mp_post)
        try:
            ds.get()
            assert False
        except RuntimeError:
            assert True

    @pytest.mark.parametrize(
        'rid,data',
        [
            ('one', {'one': 1}),
        ],
    )
    def test_data_store_organization_add(self, rid: str, data: dict, tcex: 'TcEx'):
        """Test organization datastore add

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        ds = tcex.v2.datastore('organization', self.data_type)

        results = ds.add(rid=rid, data=data)
        assert results.get('_id') == rid
        assert results.get('_shards').get('successful') == 1

    def test_data_store_organization_delete(self, tcex: 'TcEx'):
        """Test organization datastore delete

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        rid = 'three'

        ds = tcex.v2.datastore('organization', self.data_type)

        # add entry to be deleted
        ds.add(rid, {'three': 3})

        # delete
        results = ds.delete(rid=rid)
        assert results.get('_id') == rid
        assert results.get('_shards').get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_data_store_organization_get(self, tcex: 'TcEx'):
        """Test organization datastore get

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        data = {'two': 2}
        rid = 'two'

        ds = tcex.v2.datastore('organization', self.data_type)

        # add entry to get
        ds.add(rid, data)

        results = ds.get(rid=rid)
        assert results.get('_id') == rid
        assert results.get('_source').get('two') == 2
        assert results.get('found') is True

        # delete
        ds.delete(rid)

    def test_data_store_local_put(self, tcex: 'TcEx'):
        """Test local datastore put

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
        """
        data = {'one': 1}
        rid = 'one'

        ds = tcex.v2.datastore('local', self.data_type)

        # add entry to update
        ds.add(rid, {'one': 2})

        results = ds.put(rid=rid, data=data)
        assert results.get('_id') == rid
        assert results.get('_shards').get('successful') == 1

    def test_data_store_local_put_fail(self, monkeypatch, tcex: 'TcEx'):
        """Test failure of data store local put

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.v2.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session_tc, 'post', mp_post)
        try:
            ds.update(rid=None, data=None)
            assert False
        except RuntimeError:
            assert True
