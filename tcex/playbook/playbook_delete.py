"""Playbook delete."""
# standard library
import logging
from typing import Union

# first-party
from tcex.key_value_store import KeyValueApi, KeyValueRedis
from tcex.utils.utils import Utils

# get tcex logger
logger = logging.getLogger('tcex')


class PlaybookDelete:
    """Playbook Write ABC"""

    def __init__(
        self,
        context: str,
        key_value_store: Union[KeyValueApi, KeyValueRedis],
    ):
        """Initialize the class properties."""
        self.context = context
        self.key_value_store = key_value_store

        # properties
        self.log = logger
        self.utils = Utils()

    def variable(self, key: str) -> str:
        """Delete method of CRUD operation for all data types.

        Only supported when using the Redis KV store.
        """
        data = None
        if key is not None:
            data = self.key_value_store.delete(self.context, key.strip())
        else:  # pragma: no cover
            self.log.warning('The key field was None.')
        return data
