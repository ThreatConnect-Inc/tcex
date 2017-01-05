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
        """Create key/valu pair in Redis"""
        return self._r.hset(self._hash, key, value)

    def read(self, key):
        """Read data from Redis for the provided key"""
        return self._r.hget(self._hash, key)