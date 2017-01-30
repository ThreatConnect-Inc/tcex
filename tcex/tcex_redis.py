""" standard """
""" third-party """
import redis

""" custom """


class TcExRedis(object):
    """
    """

    def __init__(self, host, port, rhash):
        """ """
        self._hash = rhash
        # self._r = redis.StrictRedis(host=host, port=port, db=0)
        self._r = redis.StrictRedis(host=host, port=port)

    def create(self, key, value):
        """Create key/value pair in Redis"""
        return self._r.hset(self._hash, key, value)

    def read(self, key):
        """Read data from Redis for the provided key"""
        data = self._r.hget(self._hash, key)
        if data is not None and not isinstance(data, unicode):  # 2to3 converts unicode to str
            data = unicode(self._r.hget(self._hash, key), 'utf-8')  # 2to3 converts unicode to str
        return data
