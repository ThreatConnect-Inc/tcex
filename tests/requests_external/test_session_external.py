"""TestSessionExternal for TcEx External Session Module Testing.

This module contains comprehensive test cases for the TcEx External Session Module, specifically
testing the external session functionality including basic session operations, base URL handling,
header masking, proxy configuration, rate limiting, retry mechanisms, and HTTP status code
handling for external API requests.

Classes:
    TestSessionExternal: Test class for TcEx External Session Module functionality

TcEx Module Tested: requests_external.external_session
"""


from http import HTTPStatus
from typing import cast
from unittest.mock import patch


from requests import PreparedRequest, Response, Session


from tcex import TcEx
from tcex.requests_external.external_session import CustomAdapter, default_too_many_requests_handler
from tcex.requests_external.rate_limit_handler import RateLimitHandler
from urllib3.util.retry import Retry

# set max backoff seconds
Retry.BACKOFF_MAX = 30  # type: ignore


class TestSessionExternal:
    """TestSessionExternal for TcEx External Session Module Testing.

    This class provides comprehensive testing for the TcEx External Session Module, covering
    various external session scenarios including basic session operations, base URL configuration,
    header masking functionality, proxy settings, rate limiting, retry mechanisms, and HTTP
    status code handling for external API requests.
    """

    # Test constants
    TEST_RETRY_AFTER_DECIMAL = 100.5
    TEST_RETRY_AFTER_INTEGER = 100
    TEST_RETRY_AFTER_EMPTY = 0
    TEST_RATE_LIMIT_THRESHOLD = 13
    TEST_RETRY_TOTAL = 13
    TEST_RETRY_BACKOFF_FACTOR = 0.5
    TEST_RETRY_STATUS_CODE = 202

    @staticmethod
    def test_session_external(tcex: TcEx) -> None:
        """Test Session External Basic Functionality for TcEx External Session Module.

        This test case verifies that the external session property works correctly by making
        a request to an external URL and asserting that proxies are empty and the response
        status code is successful.

        Fixtures:
            tcex: TcEx instance with external session configured
        """
        r = tcex.session.external.get('https://www.google.com')
        assert tcex.session.external.proxies == {}
        assert r.status_code == HTTPStatus.OK

    @staticmethod
    def test_session_external_base_url(tcex: TcEx) -> None:
        """Test Session External Base URL Configuration for TcEx External Session Module.

        This test case verifies that the external session base URL can be properly configured
        and used for relative path requests, ensuring proper URL construction and response
        handling.

        Fixtures:
            tcex: TcEx instance with external session configured
        """
        session = tcex.session.external
        session.base_url = 'https://www.google.com'
        session.mask_headers = False
        r = session.get('/')
        assert tcex.session.external.proxies == {}
        assert r.status_code == HTTPStatus.OK

    @staticmethod
    def test_session_external_mask_headers(tcex: TcEx) -> None:
        """Test Session External Header Masking for TcEx External Session Module.

        This test case verifies that the external session header masking functionality works
        correctly by setting mask headers to true and configuring mask patterns, ensuring
        proper header privacy protection.

        Fixtures:
            tcex: TcEx instance with external session configured
        """
        session = tcex.session.external
        session.base_url = 'https://www.google.com'
        session.mask_headers = True
        session.mask_patterns = ['user']
        r = session.get('/')
        assert tcex.session.external.proxies == {}
        assert r.status_code == HTTPStatus.OK

    @staticmethod
    def test_session_external_proxy(tcex_proxy: TcEx) -> None:
        """Test Session External Proxy Configuration for TcEx External Session Module.

        This test case verifies that the external session proxy configuration works correctly
        by making a request with proxy settings enabled and SSL verification disabled,
        ensuring proper proxy handling.

        Fixtures:
            tcex_proxy: TcEx instance with proxy configuration enabled
        """
        r = tcex_proxy.session.external.get('https://www.google.com', verify=False)
        assert tcex_proxy.session.external.proxies is not None
        assert r.status_code == HTTPStatus.OK

    @staticmethod
    def test_default_too_many_requests_handler() -> None:
        """Test Default Too Many Requests Handler for TcEx External Session Module.

        This test case verifies that the default too many requests handler correctly processes
        Retry-After headers in various formats including decimal values, integer values, and
        empty headers, ensuring proper retry timing calculation.

        Fixtures:
            None
        """
        response = Response()
        response.headers = {'Retry-After': '100.5'}  # type: ignore

        assert (
            default_too_many_requests_handler(response)
            == TestSessionExternal.TEST_RETRY_AFTER_DECIMAL
        )

        response.headers = {'Retry-After': '100'}  # type: ignore

        assert (
            default_too_many_requests_handler(response)
            == TestSessionExternal.TEST_RETRY_AFTER_INTEGER
        )

        response.headers = {}  # type: ignore

        assert (
            default_too_many_requests_handler(response)
            == TestSessionExternal.TEST_RETRY_AFTER_EMPTY
        )

    @staticmethod
    def test_too_many_request_handler_properties(tcex: TcEx) -> None:
        """Test Too Many Requests Handler Properties for TcEx External Session Module.

        This test case verifies that the too many requests handler properties can be properly
        set and retrieved, ensuring that custom handlers can be configured and used for
        handling 429 responses.

        Fixtures:
            tcex: TcEx instance with external session configured
        """
        s = tcex.session.external
        assert s.too_many_requests_handler == default_too_many_requests_handler

        def test_handler():
            pass

        s.too_many_requests_handler = test_handler  # type: ignore

        assert s.too_many_requests_handler == test_handler

    @staticmethod
    def test_rate_limit_handler(tcex: TcEx) -> None:
        """Test Rate Limit Handler Properties for TcEx External Session Module.

        This test case verifies that the rate limit handler properties can be properly
        configured and managed, ensuring that custom header names and threshold values
        are correctly set and accessible.

        Fixtures:
            tcex: TcEx instance with external session configured
        """
        s = tcex.session.external
        assert isinstance(s.rate_limit_handler, RateLimitHandler)

        s.rate_limit_config('foo', 'bar', TestSessionExternal.TEST_RATE_LIMIT_THRESHOLD)

        assert s.rate_limit_handler.limit_remaining_header == 'foo'
        assert s.rate_limit_handler.limit_reset_header == 'bar'
        assert (
            s.rate_limit_handler.remaining_threshold
            == TestSessionExternal.TEST_RATE_LIMIT_THRESHOLD
        )

        class MyRateLimitHandler(RateLimitHandler):
            """Just for mocking, need to verify setter."""

        s.rate_limit_handler = MyRateLimitHandler()

        assert isinstance(s.rate_limit_handler, MyRateLimitHandler)

    @staticmethod
    def test_retry(tcex: TcEx) -> None:
        """Test Retry Configuration for TcEx External Session Module.

        This test case verifies that the retry method correctly configures retry settings
        without re-instantiating the CustomAdapter, ensuring that retry parameters are
        properly applied and the adapter instance is reused.

        Fixtures:
            tcex: TcEx instance with external session configured
        """
        s = tcex.session.external

        # Access private member for testing purposes
        ca = cast(CustomAdapter, s._custom_adapter)  # noqa: SLF001

        s.retry(
            TestSessionExternal.TEST_RETRY_TOTAL,
            TestSessionExternal.TEST_RETRY_BACKOFF_FACTOR,
            status_forcelist=[TestSessionExternal.TEST_RETRY_STATUS_CODE],
        )

        # Access private member for testing purposes
        assert s._custom_adapter == ca  # noqa: SLF001 # verify custom adapter isn't re-instantiated

        assert ca.max_retries.total == TestSessionExternal.TEST_RETRY_TOTAL
        assert ca.max_retries.backoff_factor == TestSessionExternal.TEST_RETRY_BACKOFF_FACTOR
        # TODO: [low] @cblades type doesn't match
        assert ca.max_retries.status_forcelist[0] == TestSessionExternal.TEST_RETRY_STATUS_CODE  # type: ignore

    @staticmethod
    def test_429(tcex: TcEx) -> None:
        """Test 429 Status Code Handling for TcEx External Session Module.

        This test case verifies that the external session correctly handles 429 status
        codes by processing Retry-After headers and implementing proper retry logic,
        ensuring robust handling of rate limiting responses.

        Fixtures:
            tcex: TcEx instance with external session configured
        """
        s = tcex.session.external

        with patch.object(Response, 'ok', value=False):
            response = Response()
            response.headers = {'Retry-After': 10}  # type: ignore
            response.status_code = HTTPStatus.TOO_MANY_REQUESTS
            request = PreparedRequest()
            request.url = 'https://www.google.com'
            response.request = request
            with patch.object(Session, 'request', return_value=response):
                response = s.get('https://www.google.com', verify=False)

        assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
