"""The RateLimitHandler implements request throttling based on X-RateLimit headers.

See https://tools.ietf.org/id/draft-polli-ratelimit-headers-00.html for implementation details.
"""
# standard library
import time
from typing import Optional

# third-party
from requests import PreparedRequest, Response

# first-party
from tcex.utils import Utils


class RateLimitHandler:
    """Rate-limiting implementation using X-RateLimit-<X> headers."""

    def __init__(
        self,
        limit_remaining_header: Optional[str] = 'X-RateLimit-Remaining',
        limit_reset_header: Optional[str] = 'X-RateLimit-Reset',
        remaining_threshold: Optional[int] = 0,
    ):
        """Rate-limiting implementation using X-RateLimit-<X> headers.

        See https://tools.ietf.org/id/draft-polli-ratelimit-headers-00.html for implementation
        details.  Uses X-RateLimit-Remaining and X-RateLimit-Reset to rate-limit requests by
        waiting until X-RateLimit-Reset when X-RateLimit-Remaining is less than or equal to
        remaining_threshold.

        Args:
            limit_remaining_header: Name of the header that has the limit remaining value.
            limit_reset_header: Name of the header that contains the limit reset value.
            remaining_threshold: Number of remaining requests available that will trigger a pause.
        """
        self._limit_remaining_header = limit_remaining_header
        self._limit_reset_header = limit_reset_header
        self._remaining_threshold = remaining_threshold

        self._last_limit_remaining_value = None
        self._last_limit_reset_value = None

    @property
    def last_limit_remaining_value(self) -> Optional[int]:
        """Get the last value received in the limit_remaining_header."""
        return self._last_limit_remaining_value

    @property
    def last_limit_reset_value(self) -> Optional[int]:
        """Get the last value received in the limit_reset_header."""
        return self._last_limit_reset_value

    @property
    def limit_remaining_header(self) -> str:
        """Get the name of the header that contains the remaining requests."""
        return self._limit_remaining_header

    @limit_remaining_header.setter
    def limit_remaining_header(self, limit_remaining_header):
        """Set the name of the header that contains the remaining requests."""
        self._limit_remaining_header = limit_remaining_header

    @property
    def limit_reset_header(self) -> str:
        """Get the name of the header that contains the rate limit reset timestamp."""
        return self._limit_reset_header

    @limit_reset_header.setter
    def limit_reset_header(self, limit_reset_header):
        self._limit_reset_header = limit_reset_header

    @property
    def remaining_threshold(self) -> int:
        """Get the threshold for remaining requests."""
        return self._remaining_threshold

    @remaining_threshold.setter
    def remaining_threshold(self, remaining_threshold: int):
        """Set the threshold for remaining requests."""
        self._remaining_threshold = remaining_threshold

    def post_send(self, response: Response) -> None:
        """Extract rate-limiting information from a response after a request has been sent.

        Args:
            response: The response from the request.  Should almost-never be modified.
        """
        if (
            response.ok
            and self.limit_remaining_header in response.headers
            and self.limit_reset_header in response.headers
        ):
            self._last_limit_remaining_value = int(
                response.headers.get(self.limit_remaining_header, 0)
            )
            self._last_limit_reset_value = response.headers.get(self.limit_reset_header)

    def pre_send(self, request: PreparedRequest) -> None:
        """Call before request is sent and provides an opportunity to pause for rate limiting.

        Compares rate-limit values from prior requests to determine if we should wait before sending
        request.  Calls self.sleep() if we should wait.

        Args:
            request: The request to be sent.  Should not be modified in any way.
        """
        if (
            self.last_limit_remaining_value is not None
            and self.last_limit_reset_value
            and self.last_limit_remaining_value <= self.remaining_threshold
        ):
            self.sleep(request)

    def sleep(self, request: PreparedRequest) -> None:  # pylint: disable=unused-argument
        """Sleeps to rate-limit.

        Sleeps until the time specified in X-RateLimit-Reset.

        Args:
            request:  The request that will be sent.
        """
        utils = Utils()
        wait_until = self.last_limit_reset_value
        try:
            seconds = (
                float(utils.datetime.format_datetime(wait_until, date_format='%s')) - time.time()
            )
        except RuntimeError:
            seconds = wait_until

        time.sleep(float(seconds))
