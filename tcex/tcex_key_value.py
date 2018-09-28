# -*- coding: utf-8 -*-
"""TcEx Framework KeyValue Module"""
from builtins import str
try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3


class TcExKeyValue(object):
    """Update Redis via ThreatConnect API Wrapper"""

    def __init__(self, tcex):
        """Initialize the Class properties.

        Args:
            tcex (object): Instance of TcEx.
            rhash (string): The REDIS hash.
        """
        self.tcex = tcex

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
        url = '/internal/playbooks/keyValue/{}'.format(key)
        r = self.tcex.session.put(url, data=value, headers=headers)
        return r.content

    # def delete(self, key):
    #     """Delete is not supported in API Wrapper"""
    #     return None

    def read(self, key):
        """Read data from remote KV store for the provided key.

        Args:
            key (string): The key to read in remote KV store.

        Returns:
            (any): The response data from the remote KV store.
        """
        key = quote(key, safe='~')
        url = '/internal/playbooks/keyValue/{}'.format(key)
        r = self.tcex.session.get(url)
        data = r.content
        if data is not None and not isinstance(data, str):
            data = str(r.content, 'utf-8')
        return data
