"""TcEx Framework Key Value API Module"""
# standard library
from typing import Any, Optional
from urllib.parse import quote


class KeyValueApi:
    """TcEx Key Value API Module.

    Args:
        session (request.Session): A configured requests session for TC API (tcex.session).
    """

    def __init__(self, context: str, session: object, runtime_level: str):
        """Initialize the Class properties."""
        self._context = context
        self._runtime_level = runtime_level
        self._session = session

    def create(self, key: str, value: Any, context: Optional[str] = None) -> str:
        """Create key/value pair in remote KV store.

        Args:
            key: The key to create in remote KV store.
            value: The value to store in remote KV store.
            context: A specific context to override the global context.

        Returns:
            (string): The response from the API call.
        """
        context = context or self._context
        key: str = quote(key, safe='~')
        headers = {'content-type': 'application/octet-stream'}
        if not context:
            raise RuntimeError(f'The provided context is invalid ({context}).')

        # this conditional is only required while there are TC instances < 6.0.7 in the wild.
        # once all TC instance are > 6.0.7 the context endpoint should work for PB Apps.
        url = f'/internal/playbooks/keyValue/{key}'
        if self._runtime_level in ['apiservice', 'triggerservice', 'webhooktriggerservice']:
            url = f'/internal/playbooks/keyValue/{context}/{key}'
        r = self._session.put(url, data=value, headers=headers)
        return r.content

    def read(self, key, context: Optional[str] = None) -> Any:
        """Read data from remote KV store for the provided key.

        Args:
            key (string): The key to read in remote KV store.
            context: A specific context to override the global context.

        Returns:
            (any): The response data from the remote KV store.
        """
        context = context or self._context
        key = quote(key, safe='~')
        if not context:
            raise RuntimeError(f'The provided context is invalid ({context}).')

        # this conditional is only required while there are TC instances < 6.0.7 in the wild.
        # once all TC instance are > 6.0.7 the context endpoint should work for PB Apps.
        url = f'/internal/playbooks/keyValue/{key}'
        if self._runtime_level in ['apiservice', 'triggerservice', 'webhooktriggerservice']:
            url = f'/internal/playbooks/keyValue/{context}/{key}'
        r = self._session.get(url)
        data = r.content
        if data is not None and not isinstance(data, str):
            data = str(r.content, 'utf-8')
        return data
