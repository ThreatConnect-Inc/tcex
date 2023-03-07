"""KeyValueABC class."""
# standard library
from abc import ABC, abstractmethod
from typing import Any


class KeyValueABC(ABC):
    """Abstract base class for all KeyValue clients."""

    @abstractmethod
    def create(self, context: str, key: str, value: Any) -> int:
        """Create key/value pair in remote KV store.

        Args:
            context: A specific context for the create.
            key: The key to create in KV store.
            value: The value to store in KV store.

        Returns:
            (string): The response from the KV store provider.
        """

    @abstractmethod
    def read(self, context: str, key: str) -> Any:
        """Read data from KV store for the provided key.

        Args:
            context: A specific context for the create.
            key: The key to read in KV store.

        Returns:
            (any): The response data from the  KV store provider.
        """
