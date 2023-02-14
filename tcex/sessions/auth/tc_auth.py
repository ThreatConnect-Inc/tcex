"""ThreatConnect Requests Session"""
# standard library
import time
from collections.abc import Callable

# first-party
from tcex.input.field_types.sensitive import Sensitive  # TYPE-CHECKING
from tcex.sessions.auth.hmac_auth import HmacAuth
from tcex.sessions.auth.token_auth import TokenAuth


class TcAuth(HmacAuth, TokenAuth):
    """ThreatConnect Token Authorization"""

    def __init__(
        self,
        tc_api_access_id: str | None = None,
        tc_api_secret_key: Sensitive | None = None,
        tc_token: Callable | str | Sensitive | None = None,
    ):
        """Initialize Class Properties."""
        # super(HmacAuth).__init__(tc_api_access_id, tc_api_secret_key)
        # super(TokenAuth, self).__init__(tc_token)
        HmacAuth.__init__(self, tc_api_access_id, tc_api_secret_key)
        TokenAuth.__init__(self, tc_token)

    def __call__(self, r):
        """Add the authorization headers to the request."""
        timestamp = int(time.time())
        if self.tc_api_access_id is not None and self.tc_api_secret_key is not None:
            r.headers['Authorization'] = self._hmac_header(r, timestamp)
        elif self.tc_token is not None:
            r.headers['Authorization'] = self._token_header()
        else:  # pragma: no cover
            raise RuntimeError('No valid ThreatConnect API credentials provided.')

        # Add required headers to auth.
        r.headers['Timestamp'] = timestamp
        return r
