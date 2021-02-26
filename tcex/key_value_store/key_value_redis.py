"""TcEx Framework Key Value Redis Module"""
# standard library
from typing import Any, Optional


class KeyValueRedis:
    """TcEx Key Value Redis Module.

    Args:
        redis_client (redis.Client): An instance of redis client.
    """

    def __init__(self, redis_client: object):
        """Initialize the Class properties."""
        self._redis_client = redis_client

    def create(self, context: str, key: str, value: Any) -> None:
        """Create key/value pair in Redis.

        Args:
            context: A specific context for the create.
            key (str): The field name (key) for the kv pair in Redis.
            value (any): The value for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self._redis_client.hset(context, key, value)

    def delete(self, context: str, key: str) -> str:
        """Alias for hdel method.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self._redis_client.hdel(context, key)

    def hgetall(self, context: str):
        """Read data from Redis for the current context.

        Args:
            context: A specific context for the create.

        Returns:
            list: The response data from Redis.
        """
        return self._redis_client.hgetall(context)

    def read(self, context: str, key: str, decode='utf-8') -> Any:
        """Read data from Redis for the provided key.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.
            decode: encoding to use to decode retrieved value or False to not decode value.

        Returns:
            str: The response data from Redis.
        """
        value = self.hget(context, key)
        # convert retrieved bytes to string
        if isinstance(value, bytes) and decode:
            value = value.decode('utf-8')
        return value

    def hget(self, context: str, key: str) -> Optional[bytes]:
        """Read data from redis for the provided key.

        This method will *not* convert the retrieved data (like read() does).

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            Optional[bytes]: the raw value from redis, if any
        """
        return self._redis_client.hget(context, key)
