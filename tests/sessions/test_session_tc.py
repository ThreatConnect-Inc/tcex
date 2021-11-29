"""Test the TcEx Session Module."""
# standard library
from typing import TYPE_CHECKING

# from tcex.sessions.auth.token_auth import TokenAuth

if TYPE_CHECKING:
    # first-party
    from tcex import TcEx


class TestUtils:
    """Test the TcEx Session Module."""

    @staticmethod
    def test_session_token_auth(tcex: 'TcEx') -> None:
        """Test tc.session property

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = tcex.session_tc.get('/v3/security/owners')

        assert r.status_code == 200

    @staticmethod
    def test_session_hmac_auth(tcex_hmac: 'TcEx') -> None:
        """Test tc.session property with hmac auth

        Args:
            tcex_hmac (TcEx, fixture): An instantiated instance of TcEx object with no token.
        """
        r = tcex_hmac.session_tc.get('/v3/security/owners')

        assert r.status_code == 200

    @staticmethod
    def test_session_proxy(tcex_proxy: 'TcEx') -> None:
        """Test tc.session property

        Args:
            tcex_proxy (TcEx, fixture): An instantiated instance of TcEx object.
        """
        tcex_proxy.session_tc.verify = False
        r = tcex_proxy.session_tc.get('/v3/security/owners')

        assert r.status_code == 200
