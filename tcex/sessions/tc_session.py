# -*- coding: utf-8 -*-
"""ThreatConnect Requests Session"""
import base64
import hashlib
import hmac
import time
import urllib3
from urllib3.util.retry import Retry
from requests import adapters, auth, Session

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class HmacAuth(auth.AuthBase):
    """ThreatConnect HMAC Authorization"""

    def __init__(self, access_id, secret_key):
        """Initialize the Class properties."""
        super(HmacAuth, self).__init__()
        self._access_id = access_id
        self._secret_key = secret_key

    def __call__(self, r):
        """Override of parent __call__ method."""
        timestamp = int(time.time())
        signature = '{}:{}:{}'.format(r.path_url, r.method, timestamp)
        hmac_signature = hmac.new(
            self._secret_key.encode(), signature.encode(), digestmod=hashlib.sha256
        ).digest()
        authorization = 'TC {}:{}'.format(
            self._access_id, base64.b64encode(hmac_signature).decode()
        )
        r.headers['Authorization'] = authorization
        r.headers['Timestamp'] = timestamp
        return r


class TokenAuth(auth.AuthBase):
    """ThreatConnect Token Authorization"""

    def __init__(self, token):
        """Initialize Class Properties."""
        super(TokenAuth, self).__init__()
        self.token = token

    def __call__(self, r):
        """Override of parent __call__ method."""
        r.headers['Authorization'] = 'TC-Token {}'.format(self.token.token)
        return r


class TcSession(Session):
    """ThreatConnect REST API Requests Session"""

    def __init__(self, tcex):
        """Initialize the Class properties."""
        super(TcSession, self).__init__()
        self.tcex = tcex
        self.args = self.tcex.default_args
        self.token = self.tcex.token

        # Add ThreatConnect Authorization
        if self._service_app or self._token_available:
            # service Apps only use tokens and playbook/runtime Apps will use token if available
            self.auth = TokenAuth(self.token)
        else:
            try:
                # for external Apps or testing Apps locally
                self.auth = HmacAuth(self.args.api_access_id, self.args.api_secret_key)
            except AttributeError:  # pragma: no cover
                raise RuntimeError('No valid ThreatConnect API credentials provided.')

        # Update User-Agent
        self.headers.update({'User-Agent': 'TcEx'})

        # Set Proxy
        if self.args.tc_proxy_tc:
            self.proxies = self.tcex.proxies
            self.tcex.log.debug(
                'Using proxy host {}:{} for ThreatConnect API.'.format(
                    self.args.tc_proxy_host, self.args.tc_proxy_port
                )
            )

        # Add Retry
        self.retry()

        # Set Verify
        self.verify = self.args.tc_verify

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
        if not url.startswith('https'):
            url = '{}{}'.format(self.args.tc_api_path, url)
        return super(TcSession, self).request(method, url, **kwargs)

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
