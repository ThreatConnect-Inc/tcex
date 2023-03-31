"""TcEx Framework Module"""
# standard library
from typing import cast
from unittest.mock import patch

# third-party
from requests import PreparedRequest, Response, Session
from urllib3.util.retry import Retry

# first-party
from tcex import TcEx
from tcex.requests_external.external_session import CustomAdapter, default_too_many_requests_handler
from tcex.requests_external.rate_limit_handler import RateLimitHandler

# set max backoff seconds
Retry.BACKOFF_MAX = 30  # type: ignore


class TestUtils:
    """Test the TcEx Session Module."""

    @staticmethod
    def test_session_external(tcex: TcEx):
        """Test tc.session_external property."""
        r = tcex.session.external.get('https://www.google.com')
        assert tcex.session.external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_base_url(tcex: TcEx):
        """Test tc.session_external property."""
        session = tcex.session.external
        session.base_url = 'https://www.google.com'
        session.mask_headers = False
        r = session.get('/')
        assert tcex.session.external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_mask_headers(tcex: TcEx):
        """Test tc.session_external property."""
        session = tcex.session.external
        session.base_url = 'https://www.google.com'
        session.mask_headers = True
        session.mask_patterns = ['user']
        r = session.get('/')
        assert tcex.session.external.proxies == {}
        assert r.status_code == 200

    @staticmethod
    def test_session_external_proxy(tcex_proxy: TcEx):
        """Test tc.session_external property with proxy."""
        r = tcex_proxy.session.external.get('https://www.google.com', verify=False)
        assert tcex_proxy.session.external.proxies is not None
        assert r.status_code == 200

    @staticmethod
    def test_default_too_many_requests_handler():
        """Test the default too many requests handler in isolation"""
        response = Response()
        response.headers = {'Retry-After': '100.5'}  # type: ignore

        assert default_too_many_requests_handler(response) == 100.5

        response.headers = {'Retry-After': '100'}  # type: ignore

        assert default_too_many_requests_handler(response) == 100

        response.headers = {}  # type: ignore

        assert default_too_many_requests_handler(response) == 0

    @staticmethod
    def test_too_many_request_handler_properties(tcex: TcEx):
        """Test the too_many_requests properties."""
        s = tcex.session.external
        # pylint: disable=comparison-with-callable
        assert s.too_many_requests_handler == default_too_many_requests_handler

        def test_handler():
            pass

        s.too_many_requests_handler = test_handler  # type: ignore

        # pylint: disable=comparison-with-callable
        assert s.too_many_requests_handler == test_handler

    @staticmethod
    def test_rate_limit_handler(tcex: TcEx):
        """Test the rate limit handler properties."""
        s = tcex.session.external
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
    def test_retry(tcex: TcEx):
        """Test the retry method to validate that it only creates one instance of CustomAdapter."""
        s = tcex.session.external

        ca = cast(CustomAdapter, s._custom_adapter)

        s.retry(13, 0.5, status_forcelist=[202])

        assert s._custom_adapter == ca  # verify custom adapter isn't re-instantiated

        assert ca.max_retries.total == 13
        assert ca.max_retries.backoff_factor == 0.5
        # TODO: [low] @cblades type doesn't match
        assert ca.max_retries.status_forcelist[0] == 202  # type: ignore

    @staticmethod
    def test_429(tcex: TcEx):
        """Test  429 handling."""
        s = tcex.session.external

        with patch.object(Response, 'ok', False):
            response = Response()
            response.headers = {'Retry-After': 10}  # type: ignore
            response.status_code = 429
            request = PreparedRequest()
            request.url = 'https://www.google.com'
            response.request = request
            with patch.object(Session, 'request', return_value=response):
                response = s.get('https://www.google.com', verify=False)

        assert response.status_code == 429

    # @staticmethod
    # def test_session_external_500_retry(tcex_proxy):
    #     """Test tc.session.external property."""
    #     session = tcex_proxy.session.external
    #     session.retry(retries=12, backoff_factor=5)
    #     session.base_url = 'https://httpbin.tci.ninja'
    #     session.mask_headers = False
    #     print('\nbefore', datetime.now().isoformat())
    #     r = session.get('/status/500', verify=False)
    #     print('\nafter', datetime.now().isoformat())
    #     print('\nr.status_code', r.status_code)
    #     # assert tcex.session.external.proxies == {}
    #     # assert r.status_code == 200
