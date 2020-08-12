# -*- coding: utf-8 -*-
"""API Handler Class"""
# standard library
import logging
import os
import threading


class ThreadFileHandler(logging.FileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(self, filename, mode='a', encoding=None, delay=0):
        """Add logic to create log directory if it does not exists.

        Args:
            filename (str): The name of the logfile.
            mode (str, optional): The write mode for the file. Defaults to 'a'.
            encoding (str, optional): The log file encoding. Defaults to None.
            delay (int, optional): The delay period. Defaults to 0.
        """
        if not os.path.exists(os.path.dirname(filename)):  # pragma: no cover
            try:
                # pylint: disable=unexpected-keyword-arg
                os.makedirs(os.path.dirname(filename), exist_ok=True)
            except TypeError:
                # TODO: [py2] - remove py2 specific code and pylint-disable
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))

        logging.FileHandler.__init__(self, filename, mode, encoding, delay)

    def emit(self, record):
        """Emit a record.

        Args:
            record (obj): The record to be logged.
        """
        if self.get_name() == threading.current_thread().name:
            logging.FileHandler.emit(self, record)
