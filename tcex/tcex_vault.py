""" standard """
import os
""" third-party """
import hvac
""" custom """


class TcExVault(object):
    """
    """

    def __init__(self, url=None, token=None, cert=None):
        """ """
        if token is None:
            token=os.environ.get('VAULT_TOKEN')
        if url is None:
            url = 'http://localhost:8200'

        self._client = hvac.Client(url=url, token=token, cert=cert)

    def create(self, key, value, lease='1h'):
        """Create key/value pair in Vault"""
        return self._client.write(key, value, lease=lease)

    def read(self, key):
        """Read data from Vault for the provided key"""
        return self._client.read(key)

    def delete(self, key):
        """Delete data from Valut for the provided key"""
        return self._client.delete(key)