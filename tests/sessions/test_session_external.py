"""Test the TcEx Session Module."""
# standard library
from unittest.mock import MagicMock, PropertyMock

# third-party
from requests import PreparedRequest, Response, Session
from urllib3.util.retry import Retry

# first-party
from tcex.sessions.external_session import default_too_many_requests_handler
from tcex.sessions.rate_limit_handler import RateLimitHandler

# set max backoff seconds
Retry.BACKOFF_MAX = 30


class TestUtils:
    """Test the TcEx Session Module."""

    @staticmethod
    def test_session_external(tcex):
        """Test tc.session_external property.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = tcex.session_external.get('https://www.google.com')
        assert tcex.session_external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_base_url(tcex):
        """Test tc.session_external property.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        session = tcex.session_external
        session.base_url = 'https://www.google.com'
        session.mask_headers = False
        r = session.get('/')
        assert tcex.session_external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_mask_headers(tcex):
        """Test tc.session_external property.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        session = tcex.session_external
        session.base_url = 'https://www.google.com'
        session.mask_headers = True
        session.mask_patterns = ['user']
        r = session.get('/')
        assert tcex.session_external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_proxy(tcex_proxy):
        """Test tc.session_external property with proxy.

        Args:
            tcex_proxy (TcEx, fixture): An instantiated instance of TcEx object.
        """
        r = tcex_proxy.session_external.get('https://www.google.com', verify=False)
        assert tcex_proxy.session_external.proxies is not None
        assert r.status_code == 200

    @staticmethod
    def test_default_too_many_requests_handler():
        """Test the default too many requests handler in isolation"""
        response: Response = Response()
        response.headers = {'Retry-After': '100.5'}

        assert default_too_many_requests_handler(response) == 100.5

        response.headers = {'Retry-After': '100'}

        assert default_too_many_requests_handler(response) == 100

        response.headers = {}

        assert default_too_many_requests_handler(response) == 0

    @staticmethod
    def test_too_many_request_handler_properties(tcex):
        """Test the too_many_requests properties

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = tcex.session_external
        # pylint: disable=comparison-with-callable
        assert s.too_many_requests_handler == default_too_many_requests_handler

        def test_handler():
            pass

        s.too_many_requests_handler = test_handler

        # pylint: disable=comparison-with-callable
        assert s.too_many_requests_handler == test_handler

    @staticmethod
    def test_rate_limit_handler(tcex):
        """Test the rate limit handler properties

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = tcex.session_external
        assert isinstance(s.rate_limit_handler, RateLimitHandler)

        s.rate_limit_config('foo', 'bar', 13)

        assert s.rate_limit_handler.limit_remaining_header == 'foo'
        assert s.rate_limit_handler.limit_reset_header == 'bar'
        assert s.rate_limit_handler.remaining_threshold == 13

        class MyRateLimitHandler(RateLimitHandler):
            """Just for mocking, need to verify setter."""

        s.rate_limit_handler = MyRateLimitHandler()

        assert isinstance(s.rate_limit_handler, MyRateLimitHandler)

    @staticmethod
    def test_retry(tcex):
        """Test the retry method to validate that it only creates one instance of CustomAdpater.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = tcex.session_external

        ca = s._custom_adapter

        s.retry(13, 0.5, status_forcelist=[202])

        assert s._custom_adapter == ca  # verify custom adapter isn't re-instantiated

        assert s._custom_adapter.max_retries.total == 13
        assert s._custom_adapter.max_retries.backoff_factor == 0.5
        assert s._custom_adapter.max_retries.status_forcelist[0] == 202

    @staticmethod
    def test_429(tcex):
        """Test  429 handling.

        Args:
            tcex (TcEx, fixture): An instantiated instance of TcEx object.
        """
        s = tcex.session_external

        response: Response = Response()
        type(response).ok = PropertyMock(False)
        response.headers = {'Retry-After': 10}
        response.status_code = 429
        request = PreparedRequest()
        request.url = 'https://www.google.com'
        response.request = request

        Session.request = MagicMock(return_value=response)

        response = s.get('https://www.google.com', verify=False)

        assert response.status_code == 429

    # @staticmethod
    # def test_session_external_500_retry(tcex_proxy):
    #     """Test tc.session_external property.

    #     Args:
    #         tcex_proxy (TcEx, fixture): An instantiated instance of TcEx object.
    #     """
    #     session = tcex_proxy.session_external
    #     session.retry(retries=12, backoff_factor=5)
    #     session.base_url = 'https://httpbin.tci.ninja'
    #     session.mask_headers = False
    #     print('\nbefore', datetime.now().isoformat())
    #     r = session.get('/status/500', verify=False)
    #     print('\nafter', datetime.now().isoformat())
    #     print('\nr.status_code', r.status_code)
    #     # assert tcex.session_external.proxies == {}
    #     # assert r.status_code == 200
