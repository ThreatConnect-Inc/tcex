"""TcEx Framework Module"""

# standard library
import logging
import time
from collections.abc import Callable

# third-party
import urllib3
from requests import Response, Session, adapters, exceptions
from requests.adapters import DEFAULT_POOLBLOCK, DEFAULT_POOLSIZE, DEFAULT_RETRIES
from urllib3.util.retry import Retry

# first-party
from tcex.requests_external.rate_limit_handler import RateLimitHandler
from tcex.util.requests_to_curl import RequestsToCurl
from tcex.util.util import Util

# get logger
_logger = logging.getLogger(__name__.split('.', maxsplit=1)[0])

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # type: ignore


def default_too_many_requests_handler(response: Response) -> float:
    """Implement 429 response handling that uses the Retry-After header.

    Will return the value in Retry-After.  See: https://tools.ietf.org/html/rfc6585#page-3.

    Assumptions:
        - Response has a Retry-After header.

    Args:
        response: The 429 response.

    Returns:
        The number of seconds to wait before sending the next request, from the Retry-After header.
    """
    util = Util()
    # the Retry-After value can be a str/int/float. as a string
    # it can be a full date (e.g., "2022-03-26T00:00:00Z")
    retry_after = response.headers.get('Retry-After', 0)
    try:
        # always convert value to seconds if possible
        seconds = util.any_to_datetime(retry_after).timestamp() - time.time()
    except RuntimeError:
        # retry_after must be in seconds
        seconds = retry_after

    # handle negative values
    if isinstance(seconds, float | int) and seconds < 0:
        seconds = retry_after

    return float(seconds)


class CustomAdapter(adapters.HTTPAdapter):
    """Custom Adapter to properly handle retries."""

    def __init__(
        self,
        rate_limit_handler: RateLimitHandler | None = None,
        pool_connections: int = DEFAULT_POOLSIZE,
        pool_maxsize: int = DEFAULT_POOLSIZE,
        max_retries: int = DEFAULT_RETRIES,
        pool_block: bool = DEFAULT_POOLBLOCK,
    ):
        """Initialize CustomAdapter.

        Args:
            rate_limit_handler: RateLimitHandler responsible for throttling.
            pool_connections: passed to super
            pool_maxsize: passed to super
            max_retries: passed to super
            pool_block: passed to super
        """
        super().__init__(pool_connections, pool_maxsize, max_retries, pool_block)
        self._rate_limit_handler = rate_limit_handler

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        """Send PreparedRequest object. Returns Response object."""
        if self.rate_limit_handler:
            self.rate_limit_handler.pre_send(request)

        try:
            response = super().send(request, stream, timeout, verify, cert, proxies)
        except exceptions.RetryError:
            # store current retries configuration
            max_retries = self.max_retries

            # temporarily disable retries and make one last request
            self.max_retries = Retry(0, read=False)

            # make request with max_retries turned off
            response = super().send(request, stream, timeout, verify, cert, proxies)

            # reset retries configuration
            self.max_retries = max_retries

        if self.rate_limit_handler:
            self.rate_limit_handler.post_send(response)

        return response

    @property
    def rate_limit_handler(self) -> RateLimitHandler | None:
        """Get the RateLimitHandler."""
        return self._rate_limit_handler

    @rate_limit_handler.setter
    def rate_limit_handler(self, rate_limit_handler: RateLimitHandler):
        """Set the RateLimitHandler."""
        self._rate_limit_handler = rate_limit_handler


class ExternalSession(Session):
    """ThreatConnect REST API Requests Session for external requests

    Args:
        base_url: The base URL for all requests.
    """

    __attrs__ = [
        'adapters',
        'auth',
        'cert',
        'cookies',
        'headers',
        'hooks',
        'max_redirects',
        'proxies',
        'params',
        'stream',
        'verify',
        'trust_env',
        # custom attrs
        '_base_url',
        '_mask_headers',
        '_mask_patterns',
        'log',
        'util',
    ]

    def __init__(self, base_url: str | None = None):
        """Initialize the Class properties."""
        super().__init__()
        self._base_url = base_url

        self._custom_adapter: CustomAdapter | None = None
        self.util = Util()

        # properties
        self._log_curl: bool = False
        self._mask_body = False
        self._mask_headers = True
        self._mask_patterns = None
        self._rate_limit_handler = RateLimitHandler()
        self._too_many_requests_handler = None
        self.log = _logger
        self.requests_to_curl = RequestsToCurl()

        # Add default Retry
        self.retry()

    @property
    def base_url(self) -> str | None:
        """Return the base url."""
        return self._base_url

    @base_url.setter
    def base_url(self, url):
        """Set base_url."""
        self._base_url = url.strip('/')

    @property
    def log_curl(self) -> bool:
        """Return whether or not requests will be logged as a curl command."""
        return self._log_curl

    @log_curl.setter
    def log_curl(self, log_curl: bool):
        """Enable or disable logging curl commands."""
        self._log_curl = log_curl

    @property
    def mask_body(self) -> bool:
        """Return property"""
        return self._mask_body

    @mask_body.setter
    def mask_body(self, mask_bool: bool):
        """Set property"""
        self._mask_body = mask_bool

    @property
    def mask_headers(self) -> bool:
        """Return property"""
        return self._mask_headers

    @mask_headers.setter
    def mask_headers(self, mask_bool: bool):
        """Set property"""
        self._mask_headers = mask_bool

    @property
    def mask_patterns(self) -> list[str] | None:
        """Return property"""
        return self._mask_patterns

    @mask_patterns.setter
    def mask_patterns(self, patterns: list):
        """Set property"""
        self._mask_patterns = patterns

    @property
    def too_many_requests_handler(self) -> Callable[[Response], float]:
        """Get the too_many_requests_handler.

        The too_many_requests_handler is responsible for determining how long to sleep (in seconds)
        on a 429 response.  The default returns the value in the `Retry-After` header.
        """
        if not self._too_many_requests_handler:
            self._too_many_requests_handler = default_too_many_requests_handler
        return self._too_many_requests_handler

    @too_many_requests_handler.setter
    def too_many_requests_handler(self, too_many_requests_handler: Callable[[Response], float]):
        """Set the too_many_requests_handler.

        The too_many_requests_handler is responsible for determining how long to sleep (in seconds)
        on a 429 response.  The default returns the value in the `Retry-After` header.

        Args:
            too_many_requests_handler: callable that returns the number of seconds to wait on a
                429 response.
        """
        self._too_many_requests_handler = too_many_requests_handler

    @property
    def rate_limit_handler(self) -> RateLimitHandler:
        """Return the RateLimitHandler.

        The RateLimitHandler is responsible for throttling request frequency.  The default
        implementation uses X-RateLimit-Remaining and X-RateLimit-Reset headers.
        """
        return self._rate_limit_handler

    @rate_limit_handler.setter
    def rate_limit_handler(self, rate_limit_handler: RateLimitHandler):
        """Set the RateLimitHandler.

        The RateLimitHandler is responsible for throttling request frequency.  The default
        implementation uses X-RateLimit-Remaining and X-RateLimit-Reset headers.

        Args:
            rate_limit_handler: the RateLimitHandler object to use.
        """
        self._rate_limit_handler = rate_limit_handler
        if self._custom_adapter:
            self._custom_adapter.rate_limit_handler = rate_limit_handler

    def request(  # pylint: disable=arguments-differ
        self, method: str, url: str, **kwargs
    ) -> object:
        """Override request method disabling verify on token renewal if disabled on session.

        Args:
            method (str): The HTTP method
            url (str): The URL or path for the request.
            kwargs: The keyword arguments to pass to the request.

        Returns:
            object: The requests Response object .
        """
        if self.base_url is not None and not url.startswith('https'):
            url = f'{self.base_url}{url}'

        # this kwargs value is used to signal 429 handling that this is a retry, but the super
        # method doesn't expect it so it needs to be removed.
        tc_is_retry = kwargs.pop('tc_is_retry', False)

        response: Response = super().request(method, url, **kwargs)

        if response.status_code == 429 and not tc_is_retry:
            too_many_requests_handler = self.too_many_requests_handler
            time.sleep(too_many_requests_handler(response))
            kwargs['tc_is_retry'] = True
            return self.request(method, url, **kwargs)

        # APP-79 - adding logging of request as curl commands
        if not response.ok or self.log_curl:
            try:
                self.log.debug(
                    self.requests_to_curl.convert(
                        response.request,
                        mask_body=self.mask_body,
                        mask_headers=self.mask_headers,
                        mask_patterns=self.mask_patterns,
                        proxies=self.proxies,
                        verify=self.verify,
                    )
                )
            except Exception:  # nosec
                pass  # logging curl command is best effort

        self.log.debug(
            f'feature=external-session, request-url={response.request.url}, '
            f'status_code={response.status_code}, elapsed={response.elapsed}'
        )

        return response

    def rate_limit_config(
        self,
        limit_remaining_header: str = 'X-RateLimit-Remaining',
        limit_reset_header: str = 'X-RateLimit-Reset',
        remaining_threshold: int = 0,
    ):
        """Configure rate-limiting.

        Configures the RateLimitHandler to use the given headers and remaining requests threshold.

        Args:
            limit_remaining_header: The header containing the number of requests remaining.
            limit_reset_header: The header that specifies when the rate limit period will reset.
            remaining_threshold: When the value in the limit_remaining_header is this value or
                lower, sleep until the time from the limit_reset_header.
        """
        self.rate_limit_handler.limit_remaining_header = limit_remaining_header
        self.rate_limit_handler.limit_reset_header = limit_reset_header
        self.rate_limit_handler.remaining_threshold = remaining_threshold

    def retry(
        self,
        retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: list | None = None,
        **kwargs,
    ):
        """Add retry to Requests Session

        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry

        Args:
            retries: The number of retry attempts.
            backoff_factor: The backoff factor for retries.
            status_forcelist: A list of status code to retry on.
            **kwargs: Additional keyword arguments to pass to the Retry object.

        Keyword Args:
            urls: An optional URL to apply the retry. If not provided the retry
                applies to all request with "https://".
        """
        retry_object = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,  # type: ignore
            status_forcelist=status_forcelist or [500, 502, 504],
        )
        urls = kwargs.get('urls') or ['https://']

        if self._custom_adapter:
            self._custom_adapter.max_retries = retry_object
        else:
            # TODO: @cblades - max_retries is typed as int and Retry is being passed
            self._custom_adapter = CustomAdapter(
                rate_limit_handler=self.rate_limit_handler, max_retries=retry_object  # type: ignore
            )

        # mount the custom adapter
        for url in urls:
            self.log.info(
                f'feature=external-session, action=applying-retry, retries={retries}, '
                f'backoff-factor={backoff_factor}, status-forcelist={status_forcelist}, url={url}'
            )
            self.mount(url, self._custom_adapter)
