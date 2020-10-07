"""API Handler Class"""
# standard library
import gzip
import os
import shutil
from logging.handlers import RotatingFileHandler
from typing import Optional


class RotatingFileHandlerCustom(RotatingFileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(
        self,
        filename: str,
        mode: Optional[str] = 'a',
        maxBytes: Optional[int] = 0,
        backupCount: Optional[int] = 0,
        encoding: Optional[str] = None,
        delay: Optional[bool] = False,
    ):
        """Customize RotatingFileHandler to create full log path.

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

        # set namer
        self.namer = self.custom_gzip_namer
        self.rotator = self.custom_gzip_rotator

    @staticmethod
    def custom_gzip_namer(name):
        """Namer for rotating log handler with gz extension.

        Args:
            name: The current name of the logfile.
        """
        return name + '.gz'

    @staticmethod
    def custom_gzip_rotator(source: str, dest: str) -> None:
        """Rotate and compress log file.

        Args:
            source: The source filename.
            dest: The destination filename.
        """
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(source)


# class RotatingFileHandlerFormatter(logging.Formatter):
#     """Custom logging formatter that allows a different format depending on the logging level."""
#
#     def __init__(self):
#         """Initialize formatter parent."""
#         super().__init__(fmt='%(levelno)d: %(msg)s', datefmt=None, style='%')
#
#     def format(self, record):
#         """Format file handle log event according to logging level.
#
#         Args:
#             record (obj): The record to be logged.
#         """
#         # Replace the original format with one customized by logging level
#         self._style._fmt = self.standard_format
#         if record.levelno < 10:  # <= logging.DEBUG
#             self._style._fmt = self.trace_format
#
#         # Call the original formatter class to do the grunt work
#         result = logging.Formatter.format(self, record)
#
#         return result
#
#     @property
#     def standard_format(self):
#         """Return the standard log format"""
#         return (
#             '%(asctime)s - %(name)s - %(levelname)s - %(message)s '
#             '(%(filename)s:%(funcName)s:%(lineno)d:%(threadName)s)'
#         )
#
#     @property
#     def trace_format(self):
#         """Return the standard log format"""
#         return (
#             '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] %(message)s '
#             '(%(filename)s:%(threadName)s)'
#         )
