"""Test the default RateLimitHandler"""
# standard library
import time
from unittest.mock import MagicMock, PropertyMock, patch

# third-party
from requests import PreparedRequest, Response

# first-party
from tcex.sessions.rate_limit_handler import RateLimitHandler


class TestRateLimitHandler:
    """Test the default RateLimitHandler"""

    @staticmethod
    @patch('time.sleep', MagicMock(return_value=None))
    @patch('time.time', MagicMock(return_value=7))
    def test_pre_send_std():
        """Test the pre_send method."""
        rate_limit_handler = RateLimitHandler()
        response: Response = Response()
        type(response).ok = PropertyMock(True)
        response.headers = {'X-RateLimit-Remaining': 0, 'X-RateLimit-Reset': 10}

        rate_limit_handler.post_send(response)

        request: PreparedRequest = PreparedRequest()

        rate_limit_handler.pre_send(request)
        time.sleep.assert_called_once_with(10)  # pylint: disable=no-member

    @staticmethod
    @patch('time.sleep', MagicMock(return_value=None))
    @patch('time.time', MagicMock(return_value=1600283000))
    def test_pre_send_timestamp():
        """Test the pre_send method."""
        rate_limit_handler = RateLimitHandler()
        response: Response = Response()
        type(response).ok = PropertyMock(True)
        response.headers = {'X-RateLimit-Remaining': 0, 'X-RateLimit-Reset': 1600284000}

        rate_limit_handler.post_send(response)
        request: PreparedRequest = PreparedRequest()

        rate_limit_handler.pre_send(request)
        time.sleep.assert_called_once_with(1000)  # pylint: disable=no-member

    @staticmethod
    @patch('time.sleep', MagicMock(return_value=None))
    @patch('time.time', MagicMock(return_value=1600283000))
    def test_pre_send_IMF_fixdate():
        """Test the pre_send method."""
        rate_limit_handler = RateLimitHandler()
        response: Response = Response()
        type(response).ok = PropertyMock(True)
        response.headers = {
            'X-RateLimit-Remaining': 0,
            'X-RateLimit-Reset': 'Wed, 16 Sep 2020 19:04:00 GMT',
        }

        rate_limit_handler.post_send(response)
        request: PreparedRequest = PreparedRequest()

        rate_limit_handler.pre_send(request)
        time.sleep.assert_called_once_with(40.0)  # pylint: disable=no-member

    @staticmethod
    def test_post_send():
        """Test the post_send method."""
        rate_limit_handler = RateLimitHandler(
            limit_remaining_header='remaining', limit_reset_header='reset'
        )

        response: Response = Response()
        type(response).ok = PropertyMock(True)
        response.headers = {
            'X-RateLimit-Remaining': 10,
            'X-RateLimit-Reset': 10,
            'remaining': 50,
            'reset': 100000,
        }

        rate_limit_handler.post_send(response)

        assert rate_limit_handler.last_limit_reset_value == 100000, 'Got wrong last reset value'
        assert rate_limit_handler.last_limit_remaining_value == 50, 'Got wrong last remaining value'

    @staticmethod
    def test_properties():
        """Test the properties."""
        rate_limit_handler = RateLimitHandler(
            limit_remaining_header='remaining', limit_reset_header='reset', remaining_threshold=12
        )

        assert rate_limit_handler.limit_remaining_header == 'remaining'
        assert rate_limit_handler.limit_reset_header == 'reset'
        assert rate_limit_handler.remaining_threshold == 12

        rate_limit_handler.limit_reset_header = 'reset2'
        rate_limit_handler.limit_remaining_header = 'remaining2'
        rate_limit_handler.remaining_threshold = 14

        assert rate_limit_handler.limit_remaining_header == 'remaining2'
        assert rate_limit_handler.limit_reset_header == 'reset2'
        assert rate_limit_handler.remaining_threshold == 14
