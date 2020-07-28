# -*- coding: utf-8 -*-
"""ThreatConnect Requests Session"""
import logging
import urllib3
from requests import Session, adapters
from urllib3.util.retry import Retry

from ..utils import Utils

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ExternalSession(Session):
    """ThreatConnect REST API Requests Session for external requests

    Args:
        logger (Logger): An instance of Logger
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

    def __init__(self, base_url=None, logger=None):
        """Initialize the Class properties."""
        super().__init__()
        self._base_url = base_url
        self.log = logger or logging.getLogger('session')

        # properties
        self._mask_headers = True
        self._mask_patterns = None
        self.utils = Utils()

        # Add default Retry
        self.retry()

    @property
    def base_url(self):
        """Return the base url."""
        return self._base_url

    @base_url.setter
    def base_url(self, url):
        """Set base_url."""
        self._base_url = url.strip('/')

    @property
    def mask_headers(self):
        """Return mask patterns."""
        return self._mask_headers

    @mask_headers.setter
    def mask_headers(self, mask_bool):
        """Return mask patterns."""
        self._mask_headers = mask_bool

    @property
    def mask_patterns(self):
        """Return mask patterns."""
        return self._mask_patterns

    @mask_patterns.setter
    def mask_patterns(self, patterns):
        """Return mask patterns."""
        self._mask_patterns = patterns

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """Override request method disabling verify on token renewal if disabled on session."""
        if self.base_url is not None and not url.startswith('https'):
            url = f'{self.base_url}{url}'
        response = super().request(method, url, **kwargs)

        # APP-79 - adding logging of request as curl commands
        self.log.debug(
            self.utils.requests_to_curl(
                response.request,
                mask_headers=self.mask_headers,
                mask_patterns=self.mask_patterns,
                proxies=self.proxies,
                verify=self.verify,
            )
        )
        self.log.debug(f'request url: {response.request.url}')
        self.log.debug(f'status_code: {response.status_code}')

        return response

    def retry(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        """Add retry to Requests Session

        https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#urllib3.util.retry.Retry
        """
        retries = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        # mount all https requests
        self.mount('https://', adapters.HTTPAdapter(max_retries=retries))
