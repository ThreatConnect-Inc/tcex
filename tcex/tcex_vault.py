# -*- coding: utf-8 -*-
""" TcEx Framework Value Module """
import os

import hvac


class TcExVault(object):
    """Add Value functionality to TcEx Framework"""

    def __init__(self, url=None, token=None, cert=None):
        """Initialize the Class properties.

        Args:
            url (string): The URL to the value server.
            token (string): The value token.
            cert (string): The value cert.
        """
        token = token or os.environ.get('VAULT_TOKEN')
        url = url or 'http://localhost:8200'
        self._client = hvac.Client(url=url, token=token, cert=cert)

    def create(self, key, value, lease='1h'):
        """Create key/value pair in Vault.

        Args:
            key (string): The data key.
            value (string): The data value.
            lease (string): The least time.
        """
        return self._client.write(key, value, lease=lease)

    def read(self, key):
        """Read data from Vault for the provided key.

        Args:
            key (string): The data key.
        """
        return self._client.read(key)

    def delete(self, key):
        """Delete data from Vault for the provided key.

        Args:
            key (string): The data key.
        """
        return self._client.delete(key)
