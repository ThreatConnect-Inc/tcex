# -*- coding: utf-8 -*-
"""ThreatConnect Requests Session"""
# standard library
import logging
from typing import Optional

# third-party
import urllib3
from requests import Session, adapters, exceptions
from urllib3.util.retry import Retry

from ..utils import Utils

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class CustomAdapter(adapters.HTTPAdapter):
    """Custom Adapter to properly handle retries."""

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        """Send PreparedRequest object. Returns Response object."""
        try:
            response = super().send(request, stream, timeout, verify, cert, proxies)
        except exceptions.RetryError:
            # store current retries configuration
            max_retries = self.max_retries

            # temporarily disable retries and max one last request
            self.max_retries = Retry(0, read=False)

            # make request with max_retries turned off
            response = super().send(request, stream, timeout, verify, cert, proxies)

            # reset retries configuration
            self.max_retries = max_retries

        return response


class ExternalSession(Session):
    """ThreatConnect REST API Requests Session for external requests

    Args:
        base_url (Optional[str] = None): The base URL for all requests.
        logger (Optional[object] = None): An instance of Logger.
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
        'utils',
    ]

    def __init__(self, base_url: Optional[str] = None, logger: Optional[object] = None):
        """Initialize the Class properties."""
        super().__init__()
        self._base_url: str = base_url
        self.log: object = logger or logging.getLogger('session')

        # properties
        self._mask_headers = True
        self._mask_patterns = None
        self.utils: object = Utils()

        # Add default Retry
        self.retry()

    @property
    def base_url(self) -> str:
        """Return the base url."""
        return self._base_url

    @base_url.setter
    def base_url(self, url):
        """Set base_url."""
        self._base_url = url.strip('/')

    @property
    def mask_headers(self) -> bool:
        """Return mask patterns."""
        return self._mask_headers

    @mask_headers.setter
    def mask_headers(self, mask_bool: bool):
        """Return mask patterns."""
        self._mask_headers = mask_bool

    @property
    def mask_patterns(self) -> list:
        """Return mask patterns."""
        return self._mask_patterns

    @mask_patterns.setter
    def mask_patterns(self, patterns: list):
        """Return mask patterns."""
        self._mask_patterns = patterns

    def request(  # pylint: disable=arguments-differ
        self, method: str, url: str, **kwargs
    ) -> object:
        """Override request method disabling verify on token renewal if disabled on session.

        Args:
            method (str): The HTTP method
            url (str): The URL or path for the request.

        Returns:
            object: The requests Response object .
        """
        if self.base_url is not None and not url.startswith('https'):
            url = f'{self.base_url}{url}'

        response: object = super().request(method, url, **kwargs)

        # APP-79 - adding logging of request as curl commands
        try:
            self.log.debug(
                self.utils.requests_to_curl(
                    response.request,
                    mask_headers=self.mask_headers,
                    mask_patterns=self.mask_patterns,
                    proxies=self.proxies,
                    verify=self.verify,
                )
            )
        except Exception:  # nosec
            pass  # logging curl command is best effort
        self.log.debug(f'request url: {response.request.url}')
        self.log.debug(f'status_code: {response.status_code}')

        return response

    def retry(
        self,
        retries: Optional[int] = 3,
        backoff_factor: Optional[float] = 0.3,
        status_forcelist: Optional[list] = None,
    ):
        """Add retry to Requests Session

        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry

        Args:
            retries (Optional[int] = 3): The number of retry attempts.
            backoff_factor (Optional[float] = 0.3): The backoff factor for retries.
            status_forcelist (Optional[list] = [500, 502, 504]): A list of status code to retry on.
        """
        retries: object = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist or [500, 502, 504],
        )
        # mount all https requests
        self.mount('https://', CustomAdapter(max_retries=retries))
