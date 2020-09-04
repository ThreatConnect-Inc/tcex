"""Test the TcEx testing Module."""
# first-party
from tcex.testing import TestCasePlaybook


# pylint: disable=no-self-use
class TestTestingSession:
    """Test TcEx testing Module."""

    def test_session_admin(self):
        """Test testing session_admin property."""
        test_case = TestCasePlaybook()
        r = test_case.session_admin.get('/v2/owners')
        assert r.status_code == 200

    def test_session_exchange(self):
        """Test testing session_admin property."""
        test_case = TestCasePlaybook()
        r = test_case.session_exchange.get('/v2/owners')
        assert r.status_code == 200
