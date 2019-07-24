# -*- coding: utf-8 -*-
"""TcEx Framework Redis Module"""
from builtins import str

import redis


class TcExRedis(object):
    """TcEx Redis Module.

    Args:
        host (str): The Redis host.
        port (str): The Redis port.
        key (str): The hash key.
    """

    def __init__(self, host, port, key):
        """Initialize the Class properties."""
        self._key = key
        self.client = redis.StrictRedis(host=host, port=port)
        self.r = self.client  # for legacy App that may have been using this value

    @property
    def key(self):
        """Return the current key."""
        return self._key

    @key.setter
    def key(self, key):
        """Set the current key."""
        self._key = key

    def blpop(self, keys, timeout=30):
        """POP a value off the first empty list in keys.

        .. note:: If timeout is 0, block will not timeout.

        Args:
            keys (str|list): The key(s) to pop the value.
            timeout (int): The number of seconds to wait before blocking stops.

        Returns:
            str: The response from Redis.
        """
        return self.client.blpop(keys, timeout)

    def create(self, field, value):
        """Create key/value pair in Redis.

        Args:
            field (str): The field name (key) for the kv pair in Redis.
            value (any): The value for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self.client.hset(self.key, field, value)

    def delete(self, field):
        """Alias for hdel method.

        Args:
            field (str): The field name (key) for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self.hdel(field)

    def hdel(self, field):
        """Delete data from Redis for the provided key.

        Args:
            field (str): The field name (key) for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self.client.hdel(self.key, field)

    def hget(self, field):
        """Read data from Redis for the provided key.

        Args:
            field (str): The field name (key) for the kv pair in Redis.

        Returns:
            str: The response data from Redis.
        """
        data = self.client.hget(self.key, field)
        if data is not None and not isinstance(data, str):
            data = str(self.client.hget(self.key, field), 'utf-8')
        return data

    def hgetall(self):
        """Read data from Redis for the provided key.

        Returns:
            str: The response data from Redis.
        """
        return self.client.hgetall(self.key)

    def hset(self, field, value):
        """Create key/value pair in Redis.

        Args:
            field (str): The field name (key) for the kv pair in Redis.
            value (any): The value for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self.client.hset(self.key, field, value)

    def read(self, field):
        """Alias for hget method."""
        return self.hget(field)

    def rpush(self, key, values):
        """Append/Push values to the end of list ``name``.

        Args:
            key (str): The channel/name to push the data.
            value (str): The values to push on the channel.

        Returns:
            str: The response from Redis.
        """
        return self.client.rpush(key, values)
