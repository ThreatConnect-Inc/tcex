"""Test the TcEx DataStore Module."""
# first-party
from tcex import TcEx
from tests.api.tc.v2.datastore.mock_post import MockPost


class TestDataStore:
    """Test the TcEx DataStore Module."""

    data_type: str

    def setup_class(self):
        """Configure setup before all tests."""
        self.data_type = 'pytest'

    def test_data_store_local_put(self, tcex: TcEx):
        """Test local datastore put

        Args:
            tcex (fixture): An instantiated instance of TcEx.
        """
        data = {'one': 1}
        rid = 'one'

        ds = tcex.api.tc.v2.datastore('local', self.data_type)

        # add entry to update
        ds.add(rid, {'one': 2})

        results = ds.put(rid=rid, data=data)
        if results is None:
            assert False, 'datastore put returned None'
        assert results.get('_id') == rid
        assert results.get('_shards', {}).get('successful') == 1

    def test_data_store_local_put_fail(self, monkeypatch, tcex: TcEx):
        """Test failure of data store local put

        Args:
            tcex (fixture): An instantiated instance of TcEx.
            monkeypatch (_pytest.monkeypatch.MonkeyPatch, fixture): Pytest monkeypatch
        """

        # monkeypatch method
        def mp_post(*args, **kwargs):  # pylint: disable=unused-argument
            return MockPost({}, ok=False)

        # delete
        ds = tcex.api.tc.v2.datastore('local', self.data_type)

        # patch after datastore created
        monkeypatch.setattr(tcex.session.tc, 'post', mp_post)
        try:
            ds.update(rid=None, data=None)  # type: ignore
            assert False
        except RuntimeError:
            assert True
