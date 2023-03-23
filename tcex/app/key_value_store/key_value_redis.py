"""TcEx Framework Key Value Redis Module"""

# third-party
from redis import Redis

# first-party
from tcex.app.key_value_store.key_value_abc import KeyValueABC


class KeyValueRedis(KeyValueABC):
    """TcEx Key Value Redis Module.

    Args:
        redis_client (redis.Client): An instance of redis client.
    """

    def __init__(self, redis_client: Redis):
        """Initialize the Class properties."""
        self.redis_client = redis_client

        # properties
        self.kv_type = 'redis'

    def create(self, context: str, key: str, value: bytes | str) -> int:
        """Create key/value pair in Redis.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.
            value: The value for the kv pair in Redis.

        Returns:
            str: The number of fields that were added.
        """
        return self.redis_client.hset(context, key, value)

    def delete(self, context: str, key: str) -> int:
        """Alias for hdel method.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        return self.redis_client.hdel(context, key)

    def get_all(self, context: str) -> dict[bytes | str, bytes | str | None]:
        """Return the contents for a given context.

        Args:
            context: the context to return
        """
        return self.hgetall(context)

    def hgetall(self, context: str) -> dict[bytes | str, bytes | str | None]:
        """Read data from Redis for the current context.

        Args:
            context: A specific context for the create.

        Returns:
            list: The response data from Redis.
        """
        return self.redis_client.hgetall(context)

    def read(self, context: str, key: str) -> bytes | str | None:
        """Read data from Redis for the provided key.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            str: The response data from Redis.
        """
        return self.hget(context, key)

    def hget(self, context: str, key: str) -> bytes | str | None:
        """Read data from redis for the provided key.

        This method will *not* convert the retrieved data (like read() does).

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            bytes | None: the raw value from redis, if any
        """
        return self.redis_client.hget(context, key)
