"""TcEx Framework Key Value Mock Module"""
# standard library
from copy import deepcopy
from threading import Lock
from typing import TYPE_CHECKING

# first-party
# first party
from tcex.key_value_store.key_value_abc import KeyValueABC

if TYPE_CHECKING:
    # standard library
    from typing import Any, Optional


class KeyValueMock(KeyValueABC):
    """TcEx Key Value Mock Module.

    Purely in-memory implementation of the KeyValueABC for local testing only.
    """

    data = {}

    def __init__(self):
        """Initialize the Class properties."""
        self.lock = Lock()
        # properties
        self.kv_type = 'mock'

    def create(self, context: str, key: str, value: 'Any') -> 'Any':
        """Create key/value pair.

        Args:
            context: A specific context for the create.
            key (str): The field name (key) for the kv pair in Redis.
            value (any): The value for the kv pair in Redis.

        Returns:
            str: The response from Redis.
        """
        with self.lock:
            self.data.setdefault(context, {})[key] = value
            return 1

    def read(self, context: str, key: str) -> 'Any':
        """Read data for the provided key.

        Args:
            context: A specific context for the create.
            key: The field name (key) for the kv pair in Redis.

        Returns:
            str: The response data from Redis.
        """
        with self.lock:
            return self.data.get(context, {}).get(key)

    def get_all(self, context: 'Optional[str]') -> 'Any':
        """Return the contents for a given context.

        Args:
            context: the context to return
        """
        if context:
            return deepcopy(self.data.get(context, []))

        return deepcopy(self.data)
