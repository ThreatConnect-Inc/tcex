"""Playbook delete."""
# standard library
import logging

# first-party
from tcex.key_value_store import KeyValueRedis
from tcex.key_value_store.key_value_abc import KeyValueABC
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module
from tcex.utils.utils import Utils

# get tcex logger
logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


class PlaybookDelete:
    """Playbook Write ABC"""

    def __init__(self, context: str, key_value_store: KeyValueABC):
        """Initialize the class properties."""
        self.context = context
        self.key_value_store = key_value_store

        # properties
        self.log = logger
        self.utils = Utils()

    def variable(self, key: str | None) -> int | None:
        """Delete method of CRUD operation for all data types.

        Only supported when using the Redis KV store.
        """
        if key is None:
            return None

        if not isinstance(self.key_value_store, KeyValueRedis):
            return None

        return self.key_value_store.delete(self.context, key.strip())
