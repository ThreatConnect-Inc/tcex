# -*- coding: utf-8 -*-
"""ThreatConnect Requests Session"""
import urllib3
from requests import Session, adapters
from urllib3.util.retry import Retry

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ExternalSession(Session):
    """ThreatConnect REST API Requests Session for external requests"""

    def __init__(self, tcex):
        """Initialize the Class properties."""
        super().__init__()
        self.tcex = tcex

        # properties
        self._base_url = None
        self._mask_headers = True
        self._mask_patterns = None

        # Update User-Agent
        self.headers.update({'User-Agent': 'TcEx'})

        # Set Proxy
        if self.tcex.default_args.tc_proxy_external:
            self.proxies = self.tcex.proxies
            self.tcex.log.info(
                'Using proxy server for external connectivity '
                f'({self.tcex.default_args.tc_proxy_host}:{self.tcex.default_args.tc_proxy_port}).'
            )

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
        return self._mask_patterns

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
        self.tcex.log.debug(
            self.tcex.utils.requests_to_curl(
                response.request,
                mask_headers=self.mask_headers,
                mask_patterns=self.mask_patterns,
                verify=self.verify,
            )
        )
        self.tcex.log.debug(f'request url: {response.request.url}')
        self.tcex.log.debug(f'status_code: {response.status_code}')

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
