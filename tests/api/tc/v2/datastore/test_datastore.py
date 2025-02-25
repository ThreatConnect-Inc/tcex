"""TcEx Framework Module"""

# standard library
import uuid

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

    @staticmethod
    def test_create_index_fail_test(tcex: TcEx, monkeypatch: MonkeyPatch):
        """Test failure to create an index."""

        # monkeypatch method
        def mp_post(*args, **kwargs):
            return MockPost({}, ok=False)

        monkeypatch.setattr(tcex.session.tc, 'post', mp_post)

        # create index
        key = str(uuid.uuid4())
        try:
            tcex.api.tc.v2.datastore('local', key)
            assert False, 'Failed to catch error on ok=False'
        except RuntimeError:
            assert True

    def test_data_store_local_index(self, tcex: TcEx):
        """Test creating a local datastore index."""
        tcex.api.tc.v2.datastore('local', self.data_type)

    @staticmethod
    def test_data_store_local_new_index(tcex: TcEx):
        """Test creating a local datastore index."""
        data = {'one': 1}
        key = str(uuid.uuid4())
        rid = 'one'

        ds = tcex.api.tc.v2.datastore('local', key)

        results = ds.add(rid=rid, data=data)
        if results is None:
            assert False, 'datastore add returned None'
        assert results.get('_id') == rid
        assert results.get('_shards', {}).get('successful') == 1
