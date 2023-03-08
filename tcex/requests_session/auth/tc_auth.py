"""ThreatConnect Requests Session"""
# standard library
import time
from collections.abc import Callable

# first-party
from tcex.app.token import Token
from tcex.input.field_types.sensitive import Sensitive  # TYPE-CHECKING
from tcex.requests_session.auth.hmac_auth import HmacAuth
from tcex.requests_session.auth.token_auth import TokenAuth


class TcAuth(HmacAuth, TokenAuth):
    """ThreatConnect Token Authorization"""

    def __init__(
        self,
        tc_api_access_id: str | None = None,
        tc_api_secret_key: Sensitive | None = None,
        tc_token: Callable | str | Sensitive | Token | None = None,
    ):
        """Initialize Class Properties."""
        if tc_api_access_id is not None and tc_api_secret_key is not None:
            HmacAuth.__init__(self, tc_api_access_id, tc_api_secret_key)
            self.auth_type = 'hmac'
        elif tc_token is not None:
            TokenAuth.__init__(self, tc_token)
            self.auth_type = 'token'
        else:  # pragma: no cover
            raise RuntimeError('No valid ThreatConnect API credentials provided.')

    def __call__(self, r):
        """Add the authorization headers to the request."""
        timestamp = int(time.time())
        if self.auth_type == 'hmac':
            r.headers['Authorization'] = self._hmac_header(r, timestamp)
        elif self.auth_type == 'token':
            r.headers['Authorization'] = self._token_header()

        # Add required headers to auth.
        r.headers['Timestamp'] = str(timestamp)
        return r
