# -*- coding: utf-8 -*-
"""ThreatConnect Requests Session"""
import base64
import hashlib
import hmac
import time

import urllib3
from requests import Session, adapters, auth
from urllib3.util.retry import Retry

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

    def __init__(self, tcex):
        """Initialize the Class properties."""
        super().__init__()
        self.tcex = tcex

        # properties
        self.args = self.tcex.default_args
        self.auth = None
        self.token = self.tcex.token

        # Update User-Agent
        self.headers.update({'User-Agent': 'TcEx'})

        # Set Proxy
        if self.args.tc_proxy_tc:
            self.proxies = self.tcex.proxies
            self.tcex.log.trace(
                f'Using proxy host {self.args.tc_proxy_host}:'
                f'{self.args.tc_proxy_port} for ThreatConnect API.'
            )

        # Add Retry
        self.retry()

        # Set Verify
        self.verify = self.args.tc_verify

    def _configure_auth(self):
        """Return Auth property for session."""
        # Add ThreatConnect Authorization
        if self._service_app or self._token_available:
            # service Apps only use tokens and playbook/runtime Apps will use token if available
            self.auth = TokenAuth(self.token)
            self.tcex.log.trace('Using token authorization.')
        elif self.args.api_access_id and self.args.api_secret_key:
            try:
                # for external Apps or testing Apps locally
                self.auth = HmacAuth(self.args.api_access_id, self.args.api_secret_key)
                self.tcex.log.trace('Using HMAC authorization.')
            except AttributeError:  # pragma: no cover
                raise RuntimeError('No valid ThreatConnect API credentials provided.')
        else:  # pragma: no cover
            raise RuntimeError('No valid ThreatConnect API credentials provided.')

    @property
    def _service_app(self):
        """Return true if the current App is a service App."""
        return self.tcex.ij.runtime_level.lower() in [
            'apiservice',
            'triggerservice',
            'webhooktriggerservice',
        ]

    @property
    def _token_available(self):
        """Return true if the current App is a service App."""
        return self.token.token is not None and self.token.token_expires is not None

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """Override request method disabling verify on token renewal if disabled on session."""
        if self.auth is None:
            self._configure_auth()

        if not url.startswith('https'):
            url = f'{self.args.tc_api_path}{url}'
        return super().request(method, url, **kwargs)

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
