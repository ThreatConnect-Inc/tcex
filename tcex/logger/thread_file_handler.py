"""API Handler Class"""
# standard library
import logging
import os
import threading
from typing import Optional


class ThreadFileHandler(logging.FileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    handler_key = None
    thread_key = None

    def __init__(
        self,
        filename: str,
        mode: Optional[str] = 'a',
        encoding: Optional[str] = None,
        delay: Optional[int] = 0,
    ):
        """Add logic to create log directory if it does not exists.

        Args:
            filename: The name of the logfile.
            mode: The write mode for the file.
            encoding: The log file encoding.
            delay: The delay period.
        """
        if not os.path.exists(os.path.dirname(filename)):  # pragma: no cover
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        logging.FileHandler.__init__(self, filename, mode, encoding, delay)

    def emit(self, record: object) -> None:
        """Emit a record.

        Emit logging events only if handler_key matches thread_key.

        Args:
            record: The record to be logged.
        """
        # handler_key and thread_key are added in logger.add_thread_file_handler() method
        if hasattr(threading.current_thread(), self.thread_key):
            if self.handler_key == getattr(threading.current_thread(), self.thread_key):
                logging.FileHandler.emit(self, record)
