# -*- coding: utf-8 -*-
"""ThreatConnect Requests Session"""
# standard library
import base64
import hashlib
import hmac
import logging
import time

# third-party
import urllib3
from requests import Session, adapters, auth
from urllib3.util.retry import Retry

from ..utils import Utils

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


class TokenAuth(auth.AuthBase):
    """ThreatConnect Token Authorization"""

    def __init__(self, token):
        """Initialize Class Properties."""
        super().__init__()
        self.token = token

    def __call__(self, r):
        """Override of parent __call__ method."""
        r.headers['Authorization'] = f'TC-Token {self.token.token}'
        return r


class TcSession(Session):
    """ThreatConnect REST API Requests Session"""

    def __init__(self, api_access_id, api_secret_key, base_url, logger=None):
        """Initialize the Class properties."""
        super().__init__()
        self.api_access_id = api_access_id
        self.api_secret_key = api_secret_key
        self.base_url = base_url.strip('/')
        self.log = logger or logging.getLogger('session')

        # properties
        self._token = None
        self.auth = None
        self.utils = Utils()

        # Add Retry
        self.retry()

    def _configure_auth(self):
        """Return Auth property for session."""
        # Add ThreatConnect Authorization
        if self.token_available:
            # service Apps only use tokens and playbook/runtime Apps will use token if available
            self.auth = TokenAuth(self.token)
            self.log.debug('Using token authorization.')
        elif self.api_access_id and self.api_secret_key:
            try:
                # for external Apps or testing Apps locally
                self.auth = HmacAuth(self.api_access_id, self.api_secret_key)
                self.log.debug('Using HMAC authorization.')
            except AttributeError:  # pragma: no cover
                raise RuntimeError('No valid ThreatConnect API credentials provided.')
        else:  # pragma: no cover
            raise RuntimeError('No valid ThreatConnect API credentials provided.')

    @property
    def token(self):
        """Return token."""
        return self._token

    @token.setter
    def token(self, token):
        """Set token."""
        self._token = token

    @property
    def token_available(self):
        """Return true if the current App is a service App."""
        return (
            self.token is not None
            and self.token.token is not None
            and self.token.token_expires is not None
        )

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """Override request method disabling verify on token renewal if disabled on session."""
        if self.auth is None:
            self._configure_auth()

        # accept path for API calls instead of full URL
        if not url.startswith('https'):
            url = f'{self.base_url}{url}'
        response = super().request(method, url, **kwargs)

        # don't show curl message for logging commands
        if '/v2/logs/app' not in url:
            # APP-79 - adding logging of request as curl commands
            try:
                self.log.debug(
                    self.utils.requests_to_curl(
                        response.request, proxies=self.proxies, verify=self.verify
                    )
                )
            except Exception:  # nosec
                pass  # logging curl command is best effort

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
