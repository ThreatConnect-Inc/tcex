# -*- coding: utf-8 -*-
"""TcEx Framework Key Value API Module"""
# standard library
from urllib.parse import quote


class KeyValueApi:
    """TcEx Key Value API Module.

    Args:
        session (request.Session): A configured requests session for TC API (tcex.session).
    """

    def __init__(self, session):
        """Initialize the Class properties."""
        self._session = session

    def create(self, key, value):
        """Create key/value pair in remote KV store.

        Args:
            key (string): The key to create in remote KV store.
            value (any): The value to store in remote KV store.

        Returns:
            (string): The response from the API call.
        """
        key = quote(key, safe='~')
        headers = {'content-type': 'application/octet-stream'}
        url = f'/internal/playbooks/keyValue/{key}'
        r = self._session.put(url, data=value, headers=headers)
        return r.content

    def read(self, key):
        """Read data from remote KV store for the provided key.

        Args:
            key (string): The key to read in remote KV store.

        Returns:
            (any): The response data from the remote KV store.
        """
        key = quote(key, safe='~')
        url = f'/internal/playbooks/keyValue/{key}'
        r = self._session.get(url)
        data = r.content
        if data is not None and not isinstance(data, str):
            data = str(r.content, 'utf-8')
        return data
