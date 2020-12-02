"""TcEx Framework Key Value Redis Module"""
# standard library
from typing import Any, Optional


class KeyValueRedis:
    """TcEx Key Value Redis Module.

    Args:
        context (str): The Redis context (hash) for hashed based operations.
        redis_client (redis.Client): An instance of redis client.
    """

    def __init__(self, context: str, redis_client: object):
        """Initialize the Class properties."""
        self._context = context
        self._redis_client = redis_client

    @property
    def context(self) -> str:
        """Return the current context."""
        return self._context

    @context.setter
    def context(self, context: str) -> None:
        """Set or update the current context."""
        self._context = context

    def create(self, key: str, value: Any, context: Optional[str] = None) -> None:
        """Create key/value pair in Redis.

        Args:
            key (str): The field name (key) for the kv pair in Redis.
            value (any): The value for the kv pair in Redis.
            context: A specific context to override the global context.

        Returns:
            str: The response from Redis.
        """
        context = context or self._context
        return self._redis_client.hset(context, key, value)

    def delete(self, key, context: Optional[str] = None) -> str:
        """Alias for hdel method.

        Args:
            key: The field name (key) for the kv pair in Redis.
            context: A specific context to override the global context.

        Returns:
            str: The response from Redis.
        """
        context = context or self._context
        return self._redis_client.hdel(self.context, key)

    def hgetall(self, context: Optional[str] = None):
        """Read data from Redis for the current context.

        Args:
            context: A specific context to override the global context.

        Returns:
            list: The response data from Redis.
        """
        context = context or self._context
        return self._redis_client.hgetall(context)

    def read(self, key: str, context: Optional[str] = None) -> Any:
        """Read data from Redis for the provided key.

        Args:
            key: The field name (key) for the kv pair in Redis.
            context: A specific context to override the global context.

        Returns:
            str: The response data from Redis.
        """
        context = context or self._context
        value = self._redis_client.hget(context, key)
        # convert retrieved bytes to string
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return value
