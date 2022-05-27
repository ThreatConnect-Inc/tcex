"""TcEx Framework Redis Module"""
# standard library
from typing import Optional

# third-party
import redis

# first-party
from tcex.backports import cached_property


class RedisClient:
    """A shared REDIS client connection using a Connection Pool.

    Initialize a single shared redis.connection.ConnectionPool.
    For a full list of kwargs see https://redis-py.readthedocs.io/en/latest/#redis.Connection.

    Args:
        host: The Redis host. Defaults to localhost.
        port: The Redis port. Defaults to 6379.
        db: The Redis db. Defaults to 0.
        blocking_pool: Use BlockingConnectionPool instead of ConnectionPool.
        errors (str, kwargs): The REDIS errors policy (e.g. strict).
        max_connections (int, kwargs): The maximum number of connections to REDIS.
        password (str, kwargs): The REDIS password.
        socket_timeout (int, kwargs): The REDIS socket timeout.
        timeout (int, kwargs): The REDIS Blocking Connection Pool timeout value.
    """

    def __init__(
        self,
        host: Optional[str] = 'localhost',
        port: Optional[int] = 6379,
        db: Optional[int] = 0,
        blocking_pool: Optional[bool] = False,
        **kwargs
    ):
        """Initialize class properties"""
        pool = redis.ConnectionPool
        if blocking_pool:
            kwargs.pop('blocking_pool')  # remove blocking_pool key
            pool = redis.BlockingConnectionPool
        self.pool = pool(host=host, port=port, db=db, **kwargs)

    @cached_property
    def client(self) -> 'redis.Redis':
        """Return an instance of redis.client.Redis."""
        return redis.Redis(connection_pool=self.pool)
