"""ThreatConnect Requests Session"""
from requests import (adapters, packages, Session)
from requests.packages.urllib3.util.retry import Retry

from .tcex_auth import (TcExHmacAuth, TcExTokenAuth)

# disable ssl warning message
packages.urllib3.disable_warnings()


class TcExSession(Session):
    """ThreatConnect REST API Requests Session"""

    def __init__(self, tcex):
        """Initialize the Class properties."""
        super(TcExSession, self).__init__()
        self.tcex = tcex
        self.args = self.tcex.default_args
        self._auth_type = 'token'
        # Add ThreatConnect Authorization
        if self.args.tc_token is not None and self.args.tc_token_expires is not None:
            self.auth = self._token_auth()
        elif self.args.api_access_id is not None and self.args.api_secret_key is not None:
            self.auth = self._hmac_auth()
            self._auth_type = 'hmac'
        else:
            raise RuntimeError('No valid ThreatConnect API credentials provided.')
        # Update User-Agent
        self.headers.update({'User-Agent': 'TcEx'})
        # Set Proxy
        if self.args.tc_proxy_tc:
            self.proxies = self.tcex.proxies
            self.tcex.log.info('Using proxy host {}:{} for ThreatConnect API.'.format(
                self.args.tc_proxy_host, self.args.tc_proxy_port))
        # Add Retry
        self.retry()
        # Verify
        self.verify = self.args.tc_verify

    def _hmac_auth(self):
        """Add ThreatConnect HMAC Auth to Session."""
        return TcExHmacAuth(self.args.api_access_id, self.args.api_secret_key, self.tcex.log)

    def _token_auth(self):
        """Add ThreatConnect Token Auth to Session."""
        return TcExTokenAuth(
            self, self.args.tc_token, self.args.tc_token_expires, self.args.tc_api_path,
            self.tcex.log)

    def request(self, method, url, **kwargs):
        """Override request method disabling verify on token renewal if disabled on session."""
        if not url.startswith('https'):
            url = '{}{}'.format(self.args.tc_api_path, url)
        return super(TcExSession, self).request(method, url, **kwargs)

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
