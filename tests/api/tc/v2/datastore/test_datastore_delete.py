"""TcEx Framework Module"""

# third-party
from _pytest.monkeypatch import MonkeyPatch

# first-party
from tcex import TcEx
from tests.api.tc.v2.datastore.mock_post import MockPost


class TestDataStore:
    """Test the TcEx DataStore Module."""

    data_type: str

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    def test_data_store_local_delete(self, tcex: TcEx):
        """Test local datastore delete."""
        rid = 'three'

        ds = tcex.api.tc.v2.datastore('local', self.data_type)

        # add entry to be deleted
        ds.add(rid, {'delete': 'delete'})

        # delete
        results = ds.delete(rid=rid)
        if results is None:
            assert False, 'datastore delete returned None'
        assert results.get('_id') == rid
        assert results.get('_shards', {}).get('successful') == 1
        assert results.get('result') == 'deleted'

    def test_data_store_local_delete_fail(self, tcex: TcEx, monkeypatch: MonkeyPatch):
        """Test failure of data store local delete."""
        rid = 'fail-test'

        # monkeypatch method
        def mp_post(*args, **kwargs):
            return MockPost({}, ok=False)

        # delete
        ds = tcex.api.tc.v2.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session.tc, 'post', mp_post)
        try:
            ds.delete(rid=rid)
            assert False
        except RuntimeError:
            assert True

    def test_data_store_organization_delete(self, tcex: TcEx):
        """Test organization datastore delete."""
        rid = 'three'

        ds = tcex.api.tc.v2.datastore('organization', self.data_type)

        # add entry to be deleted
        ds.add(rid, {'three': 3})

        # delete
        results = ds.delete(rid=rid)
        if results is None:
            assert False, 'datastore delete returned None'
        assert results.get('_id') == rid
        assert results.get('_shards', {}).get('successful') == 1
        assert results.get('result') == 'deleted'
