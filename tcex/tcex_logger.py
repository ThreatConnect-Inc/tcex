"""ThreatConnect API Logger"""
import time
from logging import Formatter, Handler


class TcExLogFormatter(Formatter):
    """Logger formatter for ThreatConnect Exchange API logging."""
    def __init__(self, task_name=None):
        """Initialize Class properties."""
        self.task_name = task_name
        super(TcExLogFormatter, self).__init__()

    def format(self, record):
        """Format log record for ThreatConnect API.

        Example log event::

            [{
                "timestamp": 1478907537000,
                "message": "Test Message",
                "level": "DEBUG"
            }]
        """
        return {
            'timestamp': int(float(record.created or time.time()) * 1000),
            'message': record.msg or '',
            'level': record.levelname or 'DEBUG'
        }


class TcExLogHandler(Handler):
    """Logger handler for ThreatConnect Exchange API logging."""

    def __init__(self, session, flush_limit=100):
        """Initialize Class properties.

        Args:
            session (Request.Session): The preconfigured instance of Session for ThreatConnect API.
            flush_limit (int): The limit to flush batch logs to the API.
        """
        super(TcExLogHandler, self).__init__()
        self.session = session
        self.flush_limit = flush_limit
        self.entries = []

    def close(self):
        """Close the logger and flush entries."""
        self.log_to_api()
        self.entries = []

    def emit(self, record):
        """Emit the log record."""
        self.entries.append(self.format(record))
        if len(self.entries) > self.flush_limit and not self.session.auth.renewing:
            self.log_to_api()
            self.entries = []

    def log_to_api(self):
        """Best effort API logger.

        Send logs to the ThreatConnect API and do nothing if the attempt fails.
        """
        if self.entries:
            try:
                headers = {'Content-Type': 'application/json'}
                self.session.post('/v2/logs/app', headers=headers, json=self.entries)
                # self.entries = []  # clear entries
            except Exception:
                # best effort on api logging
                pass
