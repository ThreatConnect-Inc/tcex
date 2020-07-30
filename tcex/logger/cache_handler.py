# -*- coding: utf-8 -*-
"""Cache Handler Class"""
# standard library
import logging


class CacheHandler(logging.Handler):
    """Logger handler for caching event until all handlers are availabe."""

    def __init__(self, max_cache=100):
        """Initialize Class properties.

        Args:
            max_cache (int): The maximum numbers of records to cache.
        """
        super().__init__()
        self.max_cache = max_cache
        self._events = []

    def emit(self, record):
        """Emit a record.

        Args:
            record (obj): The record to be logged.
        """
        # cache log events
        if len(self._events) <= self.max_cache:
            self._events.append(record)

    @property
    def events(self):
        """Return a copy and clear self._events."""
        events = list(self._events)
        self._events = []
        return events
