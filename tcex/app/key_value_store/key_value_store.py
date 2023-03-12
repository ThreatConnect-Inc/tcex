"""TcEx Module"""
# standard library
import logging
from typing import TYPE_CHECKING

# third-party
from redis import Redis

# first-party
from tcex.app.key_value_store.key_value_api import KeyValueApi
from tcex.app.key_value_store.key_value_mock import KeyValueMock
from tcex.app.key_value_store.key_value_redis import KeyValueRedis
from tcex.app.key_value_store.redis_client import RedisClient
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module
from tcex.pleb.scoped_property import scoped_property
from tcex.requests_session.tc_session import TcSession

if TYPE_CHECKING:
    # first-party
    from tcex.input.input import Input

# get tcex logger
logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


class KeyValueStore:
    """TcEx Module"""

    # TODO: @bcs - only needs model_unresolved
    def __init__(self, inputs: 'Input', session_tc: TcSession):
        """Initialize the class properties."""
        self.inputs = inputs
        self.session_tc = session_tc

        # properties
        self.log = logger

    @scoped_property
    def client(self) -> KeyValueApi | KeyValueMock | KeyValueRedis:
        """Return the correct KV store for this execution.

        The TCKeyValueAPI KV store is limited to two operations (create and read),
        while the Redis kvstore wraps a few other Redis methods.
        """
        if self.inputs.model_unresolved.tc_kvstore_type == 'Redis':
            return KeyValueRedis(self.redis_client)

        if self.inputs.model_unresolved.tc_kvstore_type == 'TCKeyValueAPI':
            return KeyValueApi(self.session_tc)  # pylint: disable=no-member

        if self.inputs.model_unresolved.tc_kvstore_type == 'Mock':
            self.log.warning(
                'Using mock key-value store. '
                'This should *never* happen when running in-platform.'
            )
            return KeyValueMock()

        raise RuntimeError(
            f'Invalid KV Store Type: ({self.inputs.model_unresolved.tc_kvstore_type})'
        )

    @staticmethod
    def get_redis_client(
        host: str, port: int, db: int = 0, blocking_pool: bool = False, **kwargs
    ) -> Redis:
        """Return a *new* instance of Redis client.

        For a full list of kwargs see https://redis-py.readthedocs.io/en/latest/#redis.Connection.

        Args:
            host: The REDIS host. Defaults to localhost.
            port: The REDIS port. Defaults to 6379.
            db: The REDIS db. Defaults to 0.
            blocking_pool: Use BlockingConnectionPool instead of ConnectionPool.
            errors (str, kwargs): The REDIS errors policy (e.g. strict).
            max_connections (int, kwargs): The maximum number of connections to REDIS.
            password (str, kwargs): The REDIS password.
            socket_timeout (int, kwargs): The REDIS socket timeout.
            timeout (int, kwargs): The REDIS Blocking Connection Pool timeout value.
        """
        return RedisClient(
            host=host, port=port, db=db, blocking_pool=blocking_pool, **kwargs
        ).client

    @scoped_property
    def redis_client(self) -> Redis:
        """Return redis client instance configure for Playbook/Service Apps."""
        return self.get_redis_client(
            host=self.inputs.model_unresolved.tc_kvstore_host,
            port=self.inputs.model_unresolved.tc_kvstore_port,
            db=0,
        )
