# -*- coding: utf-8 -*-
""" TcEx Framework KeyValue Module """
from builtins import str
try:
    from urllib import quote  # Python 2
except ImportError:
    from urllib.parse import quote  # Python 3


class TcExKeyValue(object):
    """Update Redis via ThreatConnect API Wrapper"""

    def __init__(self, tcex, rhash):
        """ """
        self._tcex = tcex
        self._hash = rhash
        self._r = tcex.request_tc()

    def create(self, key, value):
        """Create key/value pair in Redis"""
        key = quote(key, safe='~')
        self._r.body = value
        self._r.content_type = 'application/octet-stream'
        self._r.http_method = 'PUT'
        self._r.url = '{}/internal/playbooks/keyValue/{}'.format(
            self._tcex.default_args.tc_api_path, key)
        response = self._r.send()
        return response.content

    def delete(self, key):
        """Delete is not supported in API Wrapper"""
        return None

    def read(self, key):
        """Read data from Redis for the provided key"""
        key = quote(key, safe='~')
        self._r.url = '{}/internal/playbooks/keyValue/{}'.format(
            self._tcex.default_args.tc_api_path, key)
        response = self._r.send()

        data = response.content
        if data is not None and not isinstance(data, str):
            data = str(response.content, 'utf-8')
        return data
