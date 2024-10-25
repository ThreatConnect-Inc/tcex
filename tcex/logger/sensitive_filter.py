"""TcEx Framework Module"""

# standard library
import logging
from threading import Lock


class SensitiveFilter(logging.Filter):
    """Sensitive Log Filter"""

    def __init__(self, name=''):
        """Plug in a new filter to an existing formatter"""
        super().__init__(name)
        self._sensitive_registry = set()
        self._lock = Lock()

    def add(self, value: str):
        """Add sensitive value to registry."""
        if value:
            with self._lock:
                # don't add empty string
                self._sensitive_registry.add(str(value))

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter the record"""
        # have to sniff the msg and args values of the LogRecord
        record.msg = self.replace(record.getMessage())
        record.args = {}
        return True

    def replace(self, obj: str):
        """Replace any sensitive data in the object if its a string"""
        with self._lock:
            for replacement in self._sensitive_registry:
                obj = obj.replace(replacement, '***')
        return obj
