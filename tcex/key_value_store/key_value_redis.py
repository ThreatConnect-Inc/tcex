"""TcEx Framework Key Value Redis Module"""
# standard library
from typing import TYPE_CHECKING, Any, Optional

# first-party
# first party
from tcex.key_value_store.key_value_abc import KeyValueABC

if TYPE_CHECKING:
    # first-party
    from tcex.key_value_store.redis_client import RedisClient


class KeyValueRedis(KeyValueABC):
    """TcEx Key Value Redis Module.

    Args:
        redis_client (redis.Client): An instance of redis client.
    """

    def __init__(self, redis_client: 'RedisClient'):
        """Initialize the Class properties."""
        self.redis_client = redis_client

        # properties
        self.kv_type = 'redis'

    def create(self, context: str, key: str, value: Any):
        """Create key/value pair in Redis.

        Args:
            context: A specific context for the create.
            key (str): The field name (key) for the kv pair in Redis.
            value (any): The value for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self.redis_client.hset(context, key, value)

    def delete(self, context: str, key: str) -> str:
        """Alias for hdel method.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self.redis_client.hdel(context, key)

    def hgetall(self, context: str):
        """Read data from Redis for the current context.

        Args:
            context: A specific context for the create.

        Returns:
            list: The response data from Redis.
        """
        return self.redis_client.hgetall(context)

    def read(self, context: str, key: str) -> Any:
        """Read data from Redis for the provided key.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            str: The response data from Redis.
        """
        return self.hget(context, key)

    def hget(self, context: str, key: str) -> Optional[bytes]:
        """Read data from redis for the provided key.

        This method will *not* convert the retrieved data (like read() does).

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            Optional[bytes]: the raw value from redis, if any
        """
        return self.redis_client.hget(context, key)
