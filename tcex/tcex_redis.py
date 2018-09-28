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
        self.hash = rhash
        self.r = redis.StrictRedis(host=host, port=port)

    def blpop(self, keys, timeout=30):
        """RPOP a value off the first empty list in keys.

        .. note:: If timeout is 0, the block indefinitely.

        Args:
            keys (string|list): The key(s) to pop the value.
            timeout (int): The number of seconds to wait before blocking stops.

        Returns:
            (string): The response from Redis.
        """
        return self.r.blpop(keys, timeout)

    def create(self, key, value):
        """Create key/value pair in Redis.

        Args:
            key (string): The key to create in Redis.
            value (any): The value to store in Redis.

        Returns:
            (string): The response from Redis.
        """
        return self.r.hset(self.hash, key, value)

    def delete(self, key):
        """Alias for hdel method."""
        return self.hdel(key)

    def hdel(self, key):
        """Delete data from Redis for the provided key.

        Args:
            key (string): The key to delete in Redis.

        Returns:
            (string): The response from Redis.
        """
        return self.r.hdel(self.hash, key)

    def hget(self, key):
        """Read data from Redis for the provided key.

        Args:
            key (string): The key to read in Redis.

        Returns:
            (any): The response data from Redis.
        """
        data = self.r.hget(self.hash, key)
        if data is not None and not isinstance(data, str):
            data = str(self.r.hget(self.hash, key), 'utf-8')
        return data

    def hgetall(self):
        """Read data from Redis for the provided key.

        Args:
            key (string): The key to read in Redis.

        Returns:
            (any): The response data from Redis.
        """
        return self.r.hgetall(self.hash)

    def hset(self, key, value):
        """Create key/value pair in Redis.

        Args:
            key (string): The key to create in Redis.
            value (any): The value to store in Redis.

        Returns:
            (string): The response from Redis.
        """
        return self.r.hset(self.hash, key, value)

    def read(self, key):
        """Alias for hget method."""
        return self.hget(key)

    def rpush(self, name, values):
        """Append/Push values to the end of list ``name``.

        Args:
            name (string): The channel/name of the list.
            timeout (int): The number of seconds to wait before blocking stops.

        Returns:
            (string): The response from Redis.
        """
        return self.r.rpush(name, values)
