"""TcEx Framework Module"""

# standard library
import logging
import threading
import time

# third-party
from requests import Session


class ApiHandler(logging.Handler):
    """Logger handler for ThreatConnect Exchange API logging."""

    def __init__(self, session: Session, flush_limit=100):
        """Initialize instance properties.

        Args:
            session (Request.Session): The pre-configured instance of Session for ThreatConnect API.
            flush_limit (int): The limit to flush batch logs to the API.
        """
        super().__init__()
        self.session = session
        self.flush_limit = flush_limit
        self._entries = []
        self._entries_lock = threading.Lock()
        self.in_token_renewal = False

    def flush(self):
        """Close the logger and flush entries."""
        self.log_to_api(self.entries)  # pragma: no cover

    def emit(self, record: logging.LogRecord):
        """Emit a record.

        Args:
            record (obj): The record to be logged.
        """
        # TODO: [low] switch this after testing
        # if not threading.current_thread() is threading.main_thread():  # pragma: no cover
        if threading.current_thread().name != 'MainThread':  # pragma: no cover
            return

        # queue log events
        self._entries.append(self.format(record))

        # flush queue once limit is hit token module is currently renewing token
        if (
            len(self._entries) > self.flush_limit or record.levelname == 'ERROR'
        ) and not self.in_token_renewal:
            self.log_to_api(self.entries)

    def handle(self, record: logging.LogRecord):
        """Override base handle method to add logic that prevents threading deadlocks"""
        # append log entries from child threads to _entries to avoid deadlocks within handle method.
        # Otherwise, token monitor thread would try to acquire I/O lock within super().handle
        # when attempting to log messages (meaning token barrier is enabled in tokens.py).
        # if the main thread currently has the I/O lock from within super().handle and is trying
        # to retrieve a token from tokens.py to log to API, then a deadlock occurs because the
        # main thread is waiting for the barrier to be disabled, and the token thread is waiting
        # for the I/O lock from super().handle.
        if threading.current_thread().name != 'MainThread':
            with self._entries_lock:
                self._entries.append(self.format(record))
        else:
            super().handle(record)

    @property
    def entries(self):
        """Return a copy and clear self._entries."""
        with self._entries_lock:
            entries = list(self._entries)
            self._entries = []
            return entries

    def log_to_api(self, entries: list[logging.LogRecord]):
        """Send log events to the ThreatConnect API"""
        if entries:
            try:
                headers = {'Content-Type': 'application/json'}
                self.session.post('/v2/logs/app', headers=headers, json=entries)
            except Exception:  # nosec; pragma: no cover
                pass


class ApiHandlerFormatter(logging.Formatter):
    """Logger formatter for ThreatConnect Exchange API logging."""

    def __init__(self):
        """Initialize instance properties."""
        super().__init__()

    def format(self, record: logging.LogRecord):
        """Format log record for ThreatConnect API.

        Example log event::

            [{
                "timestamp": 1478907537000,
                "message": "Test Message",
                "level": "DEBUG"
            }]

        Args:
            record (obj): The record to be logged.
        """
        return {
            'timestamp': int(float(record.created or time.time()) * 1000),
            'message': record.msg or '',
            'level': record.levelname or 'DEBUG',
        }
