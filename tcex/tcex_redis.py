# -*- coding: utf-8 -*-
"""TcEx Framework Redis Module"""
from builtins import str

import redis


class TcExRedis(object):
    """Create/Read Data in/from Redis"""

    def __init__(self, host, port, rhash):
        """Initialize the Class properties.

        Args:
            host (string): The Redis host.
            port (string): The Redis port.
            rhash (string): The rhash value.
        """
        self._hash = rhash
        self._r = redis.StrictRedis(host=host, port=port)

    def create(self, key, value):
        """Create key/value pair in Redis.

        Args:
            key (string): The key to create in Redis.
            value (any): The value to store in Redis.

        Returns:
            (string): The response from Redis.
        """
        return self._r.hset(self._hash, key, value)

    def delete(self, key):
        """Delete data from Redis for the provided key.

        Args:
            key (string): The key to delete in Redis.

        Returns:
            (string): The response from Redis.
        """
        return self._r.hdel(self._hash, key)

    def read(self, key):
        """Read data from Redis for the provided key.

        Args:
            key (string): The key to read in Redis.

        Returns:
            (any): The response data from Redis.
        """
        data = self._r.hget(self._hash, key)
        if data is not None and not isinstance(data, str):
            data = str(self._r.hget(self._hash, key), 'utf-8')
        return data
