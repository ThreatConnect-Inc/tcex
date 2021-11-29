"""ThreatConnect Requests Session"""
# standard library
import time
from typing import TYPE_CHECKING, Callable, Optional, Union

# first-party
from tcex.sessions.auth.hmac_auth import HmacAuth
from tcex.sessions.auth.token_auth import TokenAuth

if TYPE_CHECKING:  # pragma: no cover
    # first-party
    from tcex.input.field_types.sensitive import Sensitive


class TcAuth(HmacAuth, TokenAuth):
    """ThreatConnect Token Authorization"""

    def __init__(
        self,
        tc_api_access_id: Optional[str] = None,
        tc_api_secret_key: Optional['Sensitive'] = None,
        tc_token: Optional[Union[Callable, str, 'Sensitive']] = None,
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
