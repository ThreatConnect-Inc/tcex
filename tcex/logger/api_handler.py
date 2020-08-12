# -*- coding: utf-8 -*-
"""API Handler Class"""
# standard library
import logging
import threading
import time


class ApiHandler(logging.Handler):
    """Logger handler for ThreatConnect Exchange API logging."""

    def __init__(self, session, flush_limit=100):
        """Initialize Class properties.

        Args:
            session (Request.Session): The preconfigured instance of Session for ThreatConnect API.
            flush_limit (int): The limit to flush batch logs to the API.
        """
        super().__init__()
        self.session = session
        self.flush_limit = flush_limit
        self._entries = []
        self.in_token_renewal = False

    def flush(self):
        """Close the logger and flush entries."""
        self.log_to_api(self.entries)  # pragma: no cover

    def emit(self, record):
        """Emit a record.

        Args:
            record (obj): The record to be logged.
        """
        if threading.current_thread().name != 'MainThread':  # pragma: no cover
            return

        # queue log events
        self._entries.append(self.format(record))

        # flush queue once limit is hit token module is currently renewing token
        if (
            len(self._entries) > self.flush_limit or record.levelname == 'ERROR'
        ) and not self.in_token_renewal:
            self.log_to_api(self.entries)

    @property
    def entries(self):
        """Return a copy and clear self._entries."""
        entries = list(self._entries)
        self._entries = []
        return entries

    def log_to_api(self, entries):
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
        """Initialize Class properties."""
        super().__init__()

    def format(self, record):
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
