""" standard """
import urllib
""" third-party """
""" custom """


class TcExKeyValue(object):
    """
    """

    def __init__(self, tcex, rhash):
        """ """
        self._tcex = tcex
        self._hash = rhash
        self._r = tcex.request_tc()

    def create(self, key, value):
        """Create key/value pair in Redis"""
        key = urllib.quote(key, safe='~')
        self._r.body = value
        self._r.content_type = 'application/octet-stream'
        self._r.http_method = 'PUT'
        self._r.url = '{}/internal/playbooks/keyValue/{}'.format(self._tcex._args.tc_api_path, key)
        response = self._r.send()
        return response.content

    def read(self, key):
        """Read data from Redis for the provided key"""
        key = urllib.quote(key, safe='~')
        self._r.url = '{}/internal/playbooks/keyValue/{}'.format(self._tcex._args.tc_api_path, key)
        response = self._r.send()

        data = response.content
        if data is not None and not isinstance(data, unicode):  # 2to3 converts unicode to str
            data = unicode(response.content, 'utf-8')  # 2to3 converts unicode to str
        return data
