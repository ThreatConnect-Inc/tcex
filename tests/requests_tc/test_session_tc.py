"""TcEx Framework Module"""

# first-party
from tcex import TcEx


class TestUtils:
    """Test the TcEx Session Module."""

    @staticmethod
    def test_session_token_auth(tcex: TcEx):
        """Test tc.session property."""
        r = tcex.session.tc.get('/v3/security/owners')

        assert r.status_code == 200

    @staticmethod
    def test_session_hmac_auth(tcex_hmac: TcEx):
        """Test tc.session property with hmac auth."""
        r = tcex_hmac.session.tc.get('/v3/security/owners')

        assert r.status_code == 200

    @staticmethod
    def test_session_proxy(tcex_proxy: TcEx):
        """Test tc.session property."""
        tcex_proxy.session.tc.verify = False
        r = tcex_proxy.session.tc.get('/v3/security/owners')

        assert r.status_code == 200
