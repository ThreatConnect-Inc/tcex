"""ThreatConnect HMAC Authorization"""
# standard library
import time
from typing import TYPE_CHECKING, Callable, Union

# third-party
from requests import auth

# first-party
from tcex.input.field_types.sensitive import Sensitive

if TYPE_CHECKING:  # pragma: no cover
    # third-party
    from requests import request


class TokenAuth(auth.AuthBase):
    """ThreatConnect HMAC Authorization"""

    def __init__(self, tc_token: Union[Callable, str, 'Sensitive']):
        """Initialize the Class properties."""
        # super().__init__()
        auth.AuthBase.__init__(self)
        self.tc_token = tc_token

    def _token_header(self):
        """Return HMAC Authorization header value."""
        _token = None
        if hasattr(self.tc_token, 'token'):
            # Token Module - The token module is provided that will handle authentication.
            _token = self.tc_token.token.value
        elif callable(self.tc_token):
            # Callabe - A callable method is provided that will return the token as a plain
            #     string. The callable will have to handle token renewal.
            _token = self.tc_token()
        elif isinstance(self.tc_token, Sensitive):
            # Sensitive - A sensitive string type was passed. Likely no support for renewal.
            _token = self.tc_token.value
        else:
            # String - A string type was passed. Likely no support for renewal.
            _token = self.tc_token

        # Return formatted token
        return f'TC-Token {_token}'

    def __call__(self, r: 'request') -> 'request':
        """Add the authorization headers to the request."""
        timestamp = int(time.time())

        # Add required headers to auth.
        r.headers['Authorization'] = self._token_header()
        r.headers['Timestamp'] = timestamp
        return r
