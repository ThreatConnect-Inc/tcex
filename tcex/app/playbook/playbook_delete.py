"""Playbook delete."""
# standard library
import logging

# first-party
from tcex.app.key_value_store import KeyValueRedis
from tcex.app.key_value_store.key_value_store import KeyValueStore
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module

# get tcex logger
logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


class PlaybookDelete:
    """Playbook Write ABC"""

    def __init__(self, context: str, key_value_store: KeyValueStore):
        """Initialize the class properties."""
        self.context = context
        self.key_value_store = key_value_store

        # properties
        self.log = logger

    def variable(self, key: str | None) -> int | None:
        """Delete method of CRUD operation for all data types.

        Only supported when using the Redis KV store.
        """
        if key is None:
            return None

        if not isinstance(self.key_value_store.client, KeyValueRedis):
            return None

        return self.key_value_store.client.delete(self.context, key.strip())
