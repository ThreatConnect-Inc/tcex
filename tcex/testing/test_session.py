# -*- coding: utf-8 -*-
"""ThreatConnect Requests Session"""
# standard library
import base64
import hashlib
import hmac
import time
from urllib.parse import quote

# third-party
import urllib3
from requests import Session, adapters, auth
from urllib3.util.retry import Retry

# first-party
from tcex.utils import Utils

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HmacAuth(auth.AuthBase):
    """ThreatConnect HMAC Authorization"""

    def __init__(self, access_id, secret_key):
        """Initialize the Class properties."""
        super().__init__()
        self._access_id = access_id
        self._secret_key = secret_key

    def __call__(self, r):
        """Override of parent __call__ method."""
        timestamp = int(time.time())
        signature = f'{r.path_url}:{r.method}:{timestamp}'
        hmac_signature = hmac.new(
            self._secret_key.encode(), signature.encode(), digestmod=hashlib.sha256
        ).digest()
        authorization = f'TC {self._access_id}:{base64.b64encode(hmac_signature).decode()}'
        r.headers['Authorization'] = authorization
        r.headers['Timestamp'] = timestamp
        return r


# APP-102 - adding ability to create sessions with different
# TC credentials for accessing special API endpoints
class TestSession(Session):
    """ThreatConnect REST API Requests Session

    Args:
        api_access_id (str): The ThreatConnect API access id.
        api_secret_key (str): The ThreatConnect API secret key.
        proxy_host (str, kwargs): The proxy hostname.
        proxy_port (int, kwargs): The proxy port number.
        proxy_user (str, kwargs): The proxy username.
        proxy_pass (str, kwargs): The proxy password.
        verify (bool, kwargs): If True SSL verification of the host will be performed.
    """

    def __init__(self, api_access_id, api_secret_key, api_path, logger, **kwargs):
        """Initialize the Class properties."""
        super().__init__()
        self.api_path = api_path
        self.api_access_id = api_access_id
        self.api_secret_key = api_secret_key
        self.log = logger
        self.proxy_host = kwargs.get('proxy_host')
        self.proxy_port = kwargs.get('proxy_port')
        self.proxy_user = kwargs.get('proxy_user')
        self.proxy_pass = kwargs.get('proxy_pass')

        # properties
        self.auth = None
        self.utils = Utils()

        # Update User-Agent
        self.headers.update({'User-Agent': 'TcEx Testing'})

        # Set Proxy
        self.proxies = self.proxy_config

        # Add Retry
        self.retry()

        # Set Verify
        self.verify = kwargs.get('verify', True)

    def _configure_auth(self):
        """Return Auth property for session."""
        if self.api_access_id and self.api_secret_key:
            try:
                # for external Apps or testing Apps locally
                self.auth = HmacAuth(self.api_access_id, self.api_secret_key)
                self.log.debug('Using HMAC authorization.')
            except AttributeError:  # pragma: no cover
                raise RuntimeError('No valid ThreatConnect API credentials provided.')
        else:  # pragma: no cover
            raise RuntimeError('No valid ThreatConnect API credentials provided.')

    @property
    def proxy_config(self):
        """Format the proxy configuration for Python Requests module.

        Generates a dictionary for use with the Python Requests module format
        when proxy is required for remote connections.

        **Example Response**
        ::

            {"http": "http://user:pass@10.10.1.10:3128/"}

        Returns:
           (dictionary): Dictionary of proxy settings
        """
        proxies = {}
        if self.proxy_host is not None and self.proxy_port is not None:

            if self.proxy_user is not None and self.proxy_pass is not None:
                proxy_user = quote(self.proxy_user, safe='~')
                proxy_pass = quote(self.proxy_pass, safe='~')

                # proxy url with auth
                proxy_url = f'{proxy_user}:{proxy_pass}' f'@{self.proxy_host}:{self.proxy_port}'
            else:
                # proxy url without auth
                proxy_url = f'{self.proxy_host}:{self.proxy_port}'
            proxies = {'http': f'http://{proxy_url}', 'https': f'https://{proxy_url}'}
        return proxies

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """Override request method disabling verify on token renewal if disabled on session."""
        if self.auth is None:
            self._configure_auth()

        if not url.startswith('https'):
            # automatically add api path to each request
            url = f'{self.api_path}{url}'
        response = super().request(method, url, **kwargs)

        # APP-79 - adding logging of request as curl commands
        self.log.debug(self.utils.requests_to_curl(response.request, verify=self.verify))

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
