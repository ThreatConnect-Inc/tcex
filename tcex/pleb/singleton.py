"""Singleton Class"""
# standard library
import os
import threading


class Singleton(type):
    """A singleton Metaclass"""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Evoke call method."""
        with cls._lock:
            if cls not in cls._instances or os.getenv('PYTEST_CURRENT_TEST') is not None:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
