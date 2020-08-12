# -*- coding: utf-8 -*-
"""TcEx Framework Redis Module"""
# third-party
import redis


class RedisClient:
    """A shared REDIS client connection using a Connection Pool.

    Initialize a single shared redis.connection.ConnectionPool.
    For a full list of kwargs see https://redis-py.readthedocs.io/en/latest/#redis.Connection.

    Args:
        host (str, optional): The REDIS host. Defaults to localhost.
        port (int, optional): The REDIS port. Defaults to 6379.
        db (int, optional): The REDIS db. Defaults to 0.
        blocking_pool (bool): Use BlockingConnectionPool instead of ConnectionPool.
        errors (str, kwargs): The REDIS errors policy (e.g. strict).
        max_connections (int, kwargs): The maximum number of connections to REDIS.
        password (str, kwargs): The REDIS password.
        socket_timeout (int, kwargs): The REDIS socket timeout.
        timeout (int, kwargs): The REDIS Blocking Connection Pool timeout value.
    """

    def __init__(self, host='localhost', port=6379, db=0, blocking_pool=False, **kwargs):
        """Initialize class properties"""
        self._client = None
        pool = redis.ConnectionPool
        if blocking_pool:
            pool = redis.BlockingConnectionPool
        self.pool = pool(host=host, port=port, db=db, **kwargs)

    @property
    def client(self):
        """Return an instance of redis.client.Redis."""
        if self._client is None:
            self._client = redis.Redis(connection_pool=self.pool)
        return self._client
