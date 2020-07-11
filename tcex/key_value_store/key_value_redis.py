# -*- coding: utf-8 -*-
"""TcEx Framework Key Value Redis Module"""


class KeyValueRedis:
    """TcEx Key Value Redis Module.

    Args:
        context (str): The Redis context (hash) for hashed based operations.
        redis_client (redis.Client): An instance of redis client.
    """

    def __init__(self, context, redis_client):
        """Initialize the Class properties."""
        self._context = context
        self._redis_client = redis_client

    @property
    def context(self):
        """Return the current context."""
        return self._context

    @context.setter
    def context(self, context):
        """Set or update the current context."""
        self._context = context

    def create(self, key, value):
        """Create key/value pair in Redis.

        Args:
            key (str): The field name (key) for the kv pair in Redis.
            value (any): The value for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self._redis_client.hset(self.context, key, value)

    def delete(self, key):
        """Alias for hdel method.

        Args:
            key (str): The field name (key) for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self._redis_client.hdel(self.context, key)

    def hgetall(self):
        """Read data from Redis for the current context.

        Returns:
            list: The response data from Redis.
        """
        return self._redis_client.hgetall(self.context)

    def read(self, key):
        """Read data from Redis for the provided key.

        Returns:
            str: The response data from Redis.
        """
        value = self._redis_client.hget(self.context, key)
        # convert retrieved bytes to string
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return value
