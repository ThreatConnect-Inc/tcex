"""Test the TcEx Session Module."""
# first-party
from tcex import TcEx


class TestUtils:
    """Test the TcEx Session Module."""

    @staticmethod
    def test_session_token_auth(tcex: TcEx):
        """Test tc.session property

        Args:
            tcex (fixture): An instantiated instance of TcEx object.
        """
        r = tcex.session.tc.get('/v3/security/owners')

        assert r.status_code == 200

    @staticmethod
    def test_session_hmac_auth(tcex_hmac: TcEx):
        """Test tc.session property with hmac auth

        Args:
            tcex_hmac (TcEx, fixture): An instantiated instance of TcEx object with no token.
        """
        r = tcex_hmac.session.tc.get('/v3/security/owners')

        assert r.status_code == 200

    @staticmethod
    def test_session_proxy(tcex_proxy: TcEx):
        """Test tc.session property

        Args:
            tcex_proxy (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex_proxy.session.tc.verify = False
        r = tcex_proxy.session.tc.get('/v3/security/owners')

        assert r.status_code == 200
