"""TestSessionTc for TcEx Session Module Testing.

This module contains comprehensive test cases for the TcEx Session Module, specifically testing
the session functionality for different authentication methods including token auth, hmac auth,
and proxy configurations.

Classes:
    TestSessionTc: Test class for TcEx Session Module functionality

TcEx Module Tested: requests_tc
"""


from http import HTTPStatus


from tcex import TcEx


class TestSessionTc:
    """TestSessionTc for TcEx Session Module Testing.

    This class provides comprehensive testing for the TcEx Session Module, covering various
    authentication methods and session configurations including token authentication, HMAC
    authentication, and proxy settings.
    """

    @staticmethod
    def test_session_token_auth(tcex: TcEx) -> None:
        """Test Session Token Authentication for TcEx Session Module.

        This test case verifies that the TcEx session property works correctly with token
        authentication by making a request to the security owners endpoint and asserting
        a successful response.

        Fixtures:
            tcex: TcEx instance with token authentication configured
        """
        r = tcex.session.tc.get('/v3/security/owners')

        assert r.status_code == HTTPStatus.OK, (
            'Expected status code 200 for successful token authentication'
        )

    @staticmethod
    def test_session_hmac_auth(tcex_hmac: TcEx) -> None:
        """Test Session HMAC Authentication for TcEx Session Module.

        This test case verifies that the TcEx session property works correctly with HMAC
        authentication by making a request to the security owners endpoint and asserting
        a successful response.

        Fixtures:
            tcex_hmac: TcEx instance with HMAC authentication configured
        """
        r = tcex_hmac.session.tc.get('/v3/security/owners')

        assert r.status_code == HTTPStatus.OK, (
            'Expected status code 200 for successful HMAC authentication'
        )

    @staticmethod
    def test_session_proxy(tcex_proxy: TcEx) -> None:
        """Test Session Proxy Configuration for TcEx Session Module.

        This test case verifies that the TcEx session property works correctly with proxy
        configuration by disabling SSL verification and making a request to the security
        owners endpoint, then asserting a successful response.

        Fixtures:
            tcex_proxy: TcEx instance with proxy configuration enabled
        """
        tcex_proxy.session.tc.verify = False
        r = tcex_proxy.session.tc.get('/v3/security/owners')

        assert r.status_code == HTTPStatus.OK, (
            'Expected status code 200 for successful proxy configuration'
        )
