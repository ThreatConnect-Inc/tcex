"""Key Value Store"""
# standard library
from typing import Union

from .key_value_api import KeyValueApi
from .key_value_redis import KeyValueRedis


def key_value_store(self, kv_type: str) -> Union[KeyValueApi, KeyValueRedis]:
    """Return the correct KV store for this execution.

    The TCKeyValueAPI KV store is limited to two operations (create and read),
    while the Redis kvstore wraps a few other Redis methods.
    """
    if kv_type == 'Redis':
        return KeyValueRedis(self.redis_client)
    elif kv_type == 'TCKeyValueAPI':
        # providing runtime_level to KeyValueApi for service Apps so that the new
        # API endpoint (in TC 6.0.7) can be used with the context. this new
        # endpoint could be used for PB Apps, however to support versions of
        # TC < 6.0.7 the old endpoint must still be used.
        return KeyValueApi(self.session, self.ij.data.runtime_level.lower())
    else:  # pragma: no cover
        raise RuntimeError(f'Invalid KV Store Type: ({kv_type})')
