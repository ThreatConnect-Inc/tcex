"""TcEx Framework Module"""
# standard library
import logging
import os
import threading
from logging.handlers import RotatingFileHandler


class ThreadFileHandler(RotatingFileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    handler_key: str
    thread_key: str

    def __init__(
        self,
        filename: str,
        mode: str = 'a',
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: str | None = None,
        delay: bool = False,
    ):
        """Add logic to create log directory if it does not exists.

        Args:
            filename: The name of the logfile.
            mode: The write mode for the file.
            maxBytes: The max file size before rotating.
            backupCount: The maximum # of backup files.
            encoding: The log file encoding.
            delay: If True, then file opening is deferred until the first call to emit().
        """
        if encoding is None and os.getenv('LANG') is None:
            encoding = 'UTF-8'
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

    def emit(self, record: logging.LogRecord):
        """Emit a record.

        Emit logging events only if handler_key matches thread_key.

        Args:
            record: The record to be logged.
        """
        # handler_key and thread_key are added in logger.add_thread_file_handler() method
        if hasattr(threading.current_thread(), self.thread_key):
            if self.handler_key == getattr(threading.current_thread(), self.thread_key):
                RotatingFileHandler.emit(self, record)
