"""Test the TcEx DataStore Module."""
# first-party
from tcex import TcEx
from tests.api.tc.v2.datastore.mock_post import MockPost


class TestDataStoreGet:
    """Test the TcEx DataStore Module."""

    data_type: str

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    def test_data_store_local_get(self, tcex: TcEx):
        """Test local datastore get

        Args:
            tcex (fixture): An instantiated instance of TcEx.
        """
        data = {'two': 2}
        rid = 'two'

        ds = tcex.v2.datastore('local', self.data_type)

        # add entry to be deleted
        ds.add(rid, data)

        results = ds.get(rid=rid)
        if results is None:
            assert False, 'datastore get returned None'
        assert results.get('_id') == rid
        assert results.get('_source', {}).get('two') == 2
        assert results.get('found') is True

        # delete
        ds.delete(rid)

    def test_data_store_local_get_no_rid(self, tcex: TcEx):
        """Test local datastore get no reid

        Args:
            tcex (fixture): An instantiated instance of TcEx.
        """
        ds = tcex.v2.datastore('local', self.data_type)

        results = ds.get()
        if results is None:
            assert False, 'datastore get returned None'
        assert results.get('hits') is not None

    def test_data_store_local_get_fail(self, tcex: TcEx, monkeypatch):
        """Test failure of data store local get

        Args:
            tcex (fixture): An instantiated instance of TcEx.
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

    def test_data_store_organization_get(self, tcex: TcEx):
        """Test organization datastore get

        Args:
            tcex (fixture): An instantiated instance of TcEx.
        """
        data = {'two': 2}
        rid = 'two'

        ds = tcex.v2.datastore('organization', self.data_type)

        # add entry to get
        ds.add(rid, data)

        results = ds.get(rid=rid)
        if results is None:
            assert False, 'datastore get returned None'
        assert results.get('_id') == rid
        assert results.get('_source', {}).get('two') == 2
        assert results.get('found') is True

        # delete
        ds.delete(rid)