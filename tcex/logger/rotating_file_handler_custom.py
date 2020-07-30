# -*- coding: utf-8 -*-
"""API Handler Class"""
# standard library
import os
from logging.handlers import RotatingFileHandler


class RotatingFileHandlerCustom(RotatingFileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        """Customize RotatingFileHandler to create full log path.

        Args:
            filename (str): The name of the logfile.
            mode (str, optional): The write mode for the file. Defaults to 'a'.
            maxBytes (int, optional): The max file size before rotating. Defaults to 0.
            backupCount (int, optional): The maximum # of backup files. Defaults to 0.
            encoding (str, optional): The log file encoding. Defaults to None.
            delay (int, optional): The delay period. Defaults to 0.
        """
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)


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
