"""Request Key File Handler Class"""
# standard library
import logging
import os
import re
import threading
from typing import Optional


class PatternFileHandler(logging.FileHandler):
    """Logger handler for ThreatConnect Exchange Pattern logging.

    This logging handler manages file limits based on a logging pattern. Given
    the pattern and max log count the handler manage the number of log files
    on disk.
    """

    def __init__(
        self,
        filename: str,
        pattern: str,
        mode: Optional[str] = 'a',
        encoding: Optional[str] = None,
        delay: Optional[bool] = False,
        max_log_count: Optional[int] = 100,
    ):
        """Add logic to create log directory if it does not exists.

        Args:
            filename: The name of the logfile.
            pattern: The pattern used to match the log files.
            mode: The write mode for the file.
            encoding: The log file encoding.
            delay: If True, then file opening is deferred until the first call to emit().
            max_log_count: The maximum number of log files to preserve.
        """
        if encoding is None and os.getenv('LANG') is None:
            encoding = 'UTF-8'

        if not os.path.exists(os.path.dirname(filename)):  # pragma: no cover
            os.makedirs(os.path.dirname(filename), exist_ok=True)

        # create pattern
        self.pattern = re.compile(pattern, re.I)

        # trim the number of logfiles to the max log count
        self._trim_log_files(filename, max_log_count)

        super().__init__(filename=filename, mode=mode, encoding=encoding, delay=delay)

    def _trim_log_files(self, filename: str, max_log_count: int) -> None:
        """Trim log files removing the oldest files.

        Args:
            filename: The logfile name.
            max_log_count: The max number of log files to keep.

        """
        log_files = []
        for entry in os.scandir(os.path.dirname(filename)):
            if not entry.is_file():
                continue

            # find only matches
            logfile_name = os.path.basename(entry.path)
            if re.match(self.pattern, logfile_name):
                log_files.append(entry)

        # sort log file entries based on modified time
        log_files.sort(key=lambda e: e.stat().st_mtime, reverse=True)

        # remove oldest logfiles
        for entry in log_files[max_log_count:]:
            try:
                os.remove(entry.path)
            except Exception:  # nosec
                # best effort
                pass

    def emit(self, record: object) -> None:
        """Emit a record.

        Emit logging events only if handler_key matches thread_key.

        Args:
            record: The record to be logged.
        """
        # handler_key and thread_key are added in logger.add_thread_file_handler() method
        # pylint: disable=no-member
        if hasattr(threading.current_thread(), self.thread_key):
            if self.handler_key == getattr(threading.current_thread(), self.thread_key):
                logging.FileHandler.emit(self, record)
