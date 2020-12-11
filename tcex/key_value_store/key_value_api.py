"""TcEx Framework Key Value API Module"""
# standard library
from typing import Any
from urllib.parse import quote


class KeyValueApi:
    """TcEx Key Value API Module.

    Args:
        session (request.Session): A configured requests session for TC API (tcex.session).
        runtime_level: The runtime level of the App.
    """

    def __init__(self, session: object, runtime_level: str):
        """Initialize the Class properties."""
        self._runtime_level = runtime_level
        self._session = session

    def create(self, context: str, key: str, value: Any) -> str:
        """Create key/value pair in remote KV store.

        Args:
            context: A specific context for the create.
            key: The key to create in remote KV store.
            value: The value to store in remote KV store.

        Returns:
            (string): The response from the API call.
        """
        key: str = quote(key, safe='~')
        headers = {'content-type': 'application/octet-stream'}

        # this conditional is only required while there are TC instances < 6.0.7 in the wild.
        # once all TC instance are > 6.0.7 the context endpoint should work for PB Apps.
        url = f'/internal/playbooks/keyValue/{key}'
        if self._runtime_level in ['apiservice', 'triggerservice', 'webhooktriggerservice']:
            url = f'/internal/playbooks/keyValue/{context}/{key}'
        r = self._session.put(url, data=value, headers=headers)
        return r.content

    def read(self, context: str, key: str) -> Any:
        """Read data from remote KV store for the provided key.

        Args:
            context: A specific context for the create.
            key: The key to read in remote KV store.

        Returns:
            (any): The response data from the remote KV store.
        """
        key = quote(key, safe='~')

        # this conditional is only required while there are TC instances < 6.0.7 in the wild.
        # once all TC instance are > 6.0.7 the context endpoint should work for PB Apps.
        url = f'/internal/playbooks/keyValue/{key}'
        if self._runtime_level in ['apiservice', 'triggerservice', 'webhooktriggerservice']:
            url = f'/internal/playbooks/keyValue/{context}/{key}'
        r = self._session.get(url)
        data = r.content

        # Binary data for PB Apps is base64 encoded, for service Apps it is not
        if data is not None and isinstance(data, bytes):
            data = data.decode('utf-8')
        return data
