"""ThreatConnect Requests Session"""
# standard library
import logging
from typing import TYPE_CHECKING, Dict, Optional, Union

# third-party
import urllib3
from requests import Session, adapters
from urllib3.util.retry import Retry

# first-party
from tcex.utils.requests_to_curl import RequestsToCurl
from tcex.utils.utils import Utils

if TYPE_CHECKING:
    # third-party
    from requests import Response

    # first-party
    from tcex.sessions.auth.hmac_auth import HmacAuth
    from tcex.sessions.auth.tc_auth import TcAuth
    from tcex.sessions.auth.token_auth import TokenAuth

# get tcex logger
logger = logging.getLogger('tcex')

# disable ssl warning message
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TcSession(Session):
    """ThreatConnect REST API Requests Session"""

    def __init__(
        self,
        auth: Union['HmacAuth', 'TokenAuth', 'TcAuth'],
        base_url: str = None,
        log_curl: Optional[bool] = False,
        proxies: Optional[Dict[str, str]] = None,
        proxies_enabled: Optional[bool] = False,
        user_agent: Optional[dict] = None,
        verify: Optional[Union[bool, str]] = True,
    ):
        """Initialize the Class properties."""
        super().__init__()
        self.base_url = base_url.strip('/')
        self.log = logger
        self.log_curl = log_curl

        # properties
        self.requests_to_curl = RequestsToCurl()
        self.utils = Utils()

        # configure auth
        self.auth = auth

        # configure optional headers
        if user_agent:
            self.headers.update(user_agent)

        # configure proxy
        if proxies and proxies_enabled:
            self.proxies = proxies

        # configure verify
        self.verify = verify

        # Add Retry
        self.retry()

    def _log_curl(self, response: 'Response'):
        """Log the curl equivalent command."""

        # don't show curl message for logging commands
        if '/v2/logs/app' not in response.request.url:

            # APP-79 - adding logging of request as curl commands
            if not response.ok or self.log_curl:
                try:
                    self.log.debug(
                        self.requests_to_curl.convert(
                            response.request, proxies=self.proxies, verify=self.verify
                        )
                    )
                except Exception:  # nosec
                    pass  # logging curl command is best effort

    def request(self, method, url, **kwargs):  # pylint: disable=arguments-differ
        """Override request method disabling verify on token renewal if disabled on session."""
        response = super().request(method, self.url(url), **kwargs)

        # retry request in case we encountered a race condition with token renewal monitor
        if response.status_code == 401:
            self.log.debug(
                f'Unexpected response received while attempting to send a request using internal '
                f'session object. Retrying request. feature=tc-session, '
                f'request-url={response.request.url}, status-code={response.status_code}'
            )
            response = super().request(method, self.url(url), **kwargs)

        # optionally log the curl command
        self._log_curl(response)

        # log request and response data
        self.log.debug(
            f'feature=tc-session, method={method}, request-url={response.request.url}, '
            f'status-code={response.status_code}, elapsed={response.elapsed}'
        )

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

    def url(self, url: str) -> str:
        """Return appropriate URL string.

        The method allows the session to accept the URL Path or the full URL.
        """
        if not url.startswith('https'):
            return f'{self.base_url}{url}'
        return url
