"""TcEx HMAC Authorization"""
# standard library
import hmac
import time
from base64 import b64encode
from hashlib import sha256
from typing import TYPE_CHECKING

# third-party
from requests import auth

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from requests import request

    # first-party
    from tcex.input.field_types.sensitive import Sensitive


class HmacAuth(auth.AuthBase):
    """ThreatConnect HMAC Authorization"""

    def __init__(self, tc_api_access_id: str, tc_api_secret_key: 'Sensitive'):
        """Initialize the Class properties."""
        # super().__init__()
        auth.AuthBase.__init__(self)
        self.tc_api_access_id = tc_api_access_id
        self.tc_api_secret_key = tc_api_secret_key

    def _hmac_header(self, r: 'request', timestamp: 'time.time'):
        """Return HMAC Authorization header value."""
        # define the signature using "full" path, HTTP method, and current timestamp
        signature = f'{r.path_url}:{r.method}:{timestamp}'

        # generate the sha256 signature using the tc secret key, encoded signature
        hmac_signature = hmac.new(
            self.tc_api_secret_key.value.encode(), signature.encode(), digestmod=sha256
        ).digest()

        # return the header value with access_id and b64 signature value
        return f'TC {self.tc_api_access_id}:{b64encode(hmac_signature).decode()}'

    def __call__(self, r: 'request') -> 'request':
        """Add the authorization headers to the request."""
        timestamp = int(time.time())

        # Add required headers to auth.
        r.headers['Authorization'] = self._hmac_header(r, timestamp)
        r.headers['Timestamp'] = timestamp
        return r
