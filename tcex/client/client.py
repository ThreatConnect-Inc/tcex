"""ThreatConnect httpx Client"""
# standard library
import base64
import hashlib
import hmac
import time

# third-party
from httpx import Auth, Client


class HmacAuth(Auth):
    """ThreatConnect HMAC Authorization"""

    def __init__(self, access_id: str, secret_key: str) -> None:
        """Initialize class properties."""
        self._access_id = access_id
        self._secret_key = secret_key

    def auth_flow(self, request):
        """Update the request object with HMAC Authorization."""
        timestamp = str(int(time.time()))
        signature = f'{request.url.path}:{request.method}:{timestamp}'
        hmac_signature = hmac.new(
            self._secret_key.encode(), signature.encode(), digestmod=hashlib.sha256
        ).digest()
        authorization = f'TC {self._access_id}:{base64.b64encode(hmac_signature).decode()}'

        # add required authorization headers
        request.headers['Authorization'] = authorization
        request.headers['Timestamp'] = timestamp

        yield request


class TokenAuth(Auth):
    """ThreatConnect Token Authorization"""

    def __init__(self, token: str) -> None:
        """Initialize class properties."""
        self._token = token

    def auth_flow(self, request):
        """Update the request object with HMAC Authorization."""
        request.headers['Authorization'] = f'TC-Token {self._token.token}'
        return request


class _Client(Client):
    """TcEx Client class for external requests."""

    def __init__(self, **kwargs):
        """Initialize the Class properties."""
        super().__init__(**kwargs)
