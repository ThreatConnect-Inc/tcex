"""TcEx Framework Key Value API Module"""
# standard library
from typing import Any
from urllib.parse import quote

# third-party
from requests import Session

# first-party
from tcex.key_value_store.key_value_abc import KeyValueABC


class KeyValueApi(KeyValueABC):
    """TcEx Key Value API Module.

    Args:
        session: A configured requests session for TC API (tcex.session).
    """

    def __init__(self, session: Session):
        """Initialize the Class properties."""
        self._session = session

        # properties
        self.kv_type = 'api'

    def create(self, context: str, key: str, value: Any) -> int:
        """Create key/value pair in remote KV store.

        Args:
            context: A specific context for the create.
            key: The key to create in remote KV store.
            value: The value to store in remote KV store.

        Returns:
            (string): The response from the API call.
        """
        key = quote(key, safe='~')
        headers = {'content-type': 'application/octet-stream'}
        url = f'/internal/playbooks/keyValue/{context}/{key}'

        r = self._session.put(url, data=value, headers=headers)
        if r.ok:
            # the redis client returns the count of items added, in this case there is only one
            return 1
        return 0  # no entries created

    def read(self, context: str, key: str) -> bytes | str | None:
        """Read data from remote KV store for the provided key.

        Args:
            context: A specific context for the create.
            key: The key to read in remote KV store.

        Returns:
            (any): The response data from the remote KV store.
        """
        key = quote(key, safe='~')

        url = f'/internal/playbooks/keyValue/{context}/{key}'
        r = self._session.get(url)
        data = r.content

        # Binary data for PB Apps is base64 encoded, for service Apps it is not
        if data is not None and isinstance(data, bytes):
            data = data.decode('utf-8')
        return data
