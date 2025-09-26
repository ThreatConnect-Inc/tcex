"""TestRateLimitHandler for TcEx Rate Limit Handler Module Testing.

This module contains comprehensive test cases for the TcEx Rate Limit Handler Module, specifically
testing the rate limiting functionality for external requests including pre-send and post-send
behaviors, timestamp handling, and custom header configurations.

Classes:
    TestRateLimitHandler: Test class for TcEx Rate Limit Handler Module functionality

TcEx Module Tested: requests_external.rate_limit_handler
"""


import time
from unittest.mock import MagicMock, patch


from requests import PreparedRequest, Response


from tcex.requests_external.rate_limit_handler import RateLimitHandler


class TestRateLimitHandler:
    """TestRateLimitHandler for TcEx Rate Limit Handler Module Testing.

    This class provides comprehensive testing for the TcEx Rate Limit Handler Module, covering
    various rate limiting scenarios including standard timestamp handling, custom timestamp
    processing, IMF fixdate parsing, post-send functionality, and property management.
    """

    # Test constants
    TEST_RESET_VALUE = 100000
    TEST_REMAINING_VALUE = 50
    TEST_THRESHOLD_1 = 12
    TEST_THRESHOLD_2 = 14

    @staticmethod
    @patch('time.sleep', MagicMock(return_value=None))
    @patch('time.time', MagicMock(return_value=7))
    def test_pre_send_std() -> None:
        """Test Pre-Send Standard Timestamp for TcEx Rate Limit Handler Module.

        This test case verifies that the pre_send method correctly handles standard timestamp
        values by calculating the appropriate sleep duration and calling time.sleep with the
        correct value when rate limiting is triggered.
        """
        rate_limit_handler = RateLimitHandler()
        response = Response()

        with patch.object(Response, 'ok', value=True):
            response.headers = {'X-RateLimit-Remaining': 0, 'X-RateLimit-Reset': 10}  # type: ignore

            rate_limit_handler.post_send(response)

            request: PreparedRequest = PreparedRequest()

            rate_limit_handler.pre_send(request)
            time.sleep.assert_called_once_with(3)  # type: ignore

    @staticmethod
    @patch('time.sleep', MagicMock(return_value=None))
    @patch('time.time', MagicMock(return_value=1600283000))
    def test_pre_send_timestamp() -> None:
        """Test Pre-Send Custom Timestamp for TcEx Rate Limit Handler Module.

        This test case verifies that the pre_send method correctly handles custom timestamp
        values by calculating the appropriate sleep duration and calling time.sleep with the
        correct value when rate limiting is triggered.
        """
        rate_limit_handler = RateLimitHandler()
        response: Response = Response()
        with patch.object(Response, 'ok', value=True):
            response.headers = {  # type: ignore
                'X-RateLimit-Remaining': 0,
                'X-RateLimit-Reset': 1600284000,
            }

            rate_limit_handler.post_send(response)
            request: PreparedRequest = PreparedRequest()

            rate_limit_handler.pre_send(request)
            time.sleep.assert_called_once_with(1000)  # type: ignore

    @staticmethod
    @patch('time.sleep', MagicMock(return_value=None))
    @patch('time.time', MagicMock(return_value=1600283000))
    def test_pre_send_imf_fixdate() -> None:
        """Test Pre-Send IMF Fixdate for TcEx Rate Limit Handler Module.

        This test case verifies that the pre_send method correctly handles IMF fixdate format
        strings by parsing the date and calculating the appropriate sleep duration, then
        calling time.sleep with the correct value when rate limiting is triggered.
        """
        rate_limit_handler = RateLimitHandler()
        response: Response = Response()
        with patch.object(Response, 'ok', value=True):
            response.headers = {  # type: ignore
                'X-RateLimit-Remaining': 0,
                'X-RateLimit-Reset': 'Wed, 16 Sep 2020 19:04:00 GMT',
            }

            rate_limit_handler.post_send(response)
            request: PreparedRequest = PreparedRequest()

            rate_limit_handler.pre_send(request)
            time.sleep.assert_called_once_with(40.0)  # type: ignore

    @staticmethod
    def test_post_send() -> None:
        """Test Post-Send Functionality for TcEx Rate Limit Handler Module.

        This test case verifies that the post_send method correctly processes response headers
        and stores the rate limiting values for future use, ensuring proper header parsing
        and value storage.
        """
        rate_limit_handler = RateLimitHandler(
            limit_remaining_header='remaining', limit_reset_header='reset'
        )

        with patch.object(Response, 'ok', value=True):
            response: Response = Response()
            response.headers = {  # type: ignore
                'X-RateLimit-Remaining': 10,
                'X-RateLimit-Reset': 10,
                'remaining': TestRateLimitHandler.TEST_REMAINING_VALUE,
                'reset': TestRateLimitHandler.TEST_RESET_VALUE,
            }

            rate_limit_handler.post_send(response)

        assert rate_limit_handler.last_limit_reset_value == TestRateLimitHandler.TEST_RESET_VALUE, (
            'Got wrong last reset value'
        )
        assert (
            rate_limit_handler.last_limit_remaining_value
            == TestRateLimitHandler.TEST_REMAINING_VALUE
        ), 'Got wrong last remaining value'

    @staticmethod
    def test_properties() -> None:
        """Test Properties Management for TcEx Rate Limit Handler Module.

        This test case verifies that the RateLimitHandler properties can be properly set and
        retrieved, ensuring that custom header names and threshold values are correctly
        managed and accessible.
        """
        rate_limit_handler = RateLimitHandler(
            limit_remaining_header='remaining',
            limit_reset_header='reset',
            remaining_threshold=TestRateLimitHandler.TEST_THRESHOLD_1,
        )

        assert rate_limit_handler.limit_remaining_header == 'remaining'
        assert rate_limit_handler.limit_reset_header == 'reset'
        assert rate_limit_handler.remaining_threshold == TestRateLimitHandler.TEST_THRESHOLD_1

        rate_limit_handler.limit_reset_header = 'reset2'
        rate_limit_handler.limit_remaining_header = 'remaining2'
        rate_limit_handler.remaining_threshold = TestRateLimitHandler.TEST_THRESHOLD_2

        assert rate_limit_handler.limit_remaining_header == 'remaining2'
        assert rate_limit_handler.limit_reset_header == 'reset2'
        assert rate_limit_handler.remaining_threshold == TestRateLimitHandler.TEST_THRESHOLD_2
