# -*- coding: utf-8 -*-
"""Trace Logger Class"""
import logging
import sys
from inspect import getframeinfo, stack

# Create trace logging level
logging.TRACE = logging.DEBUG - 5
logging.addLevelName(logging.TRACE, 'TRACE')


class TraceLogger(logging.Logger):
    """Add trace level to logging"""

    def findCaller(self, stack_info=False):
        """Find the caller for the current log event.

        Args:
            stack_info (bool, optional): Defaults to False.

        Returns:
            tuple: The caller stack information.
        """
        caller = None
        depth = 3
        while True:
            # search for the correct calling method
            caller = getframeinfo(stack()[depth][0])
            if caller.function != 'trace' or depth >= 6:
                break
            depth += 1

        if sys.version_info < (3,):
            # return value for py2
            return (caller.filename, caller.lineno, caller.function)
        # TODO: [py2] - remove py2 statement and remove coverage pragma
        return (caller.filename, caller.lineno, caller.function, None)  # pragma: no cover

    def trace(self, msg, *args, **kwargs):
        """Set trace logging level

        Args:
            msg (str): The message to be logged.
        """
        self.log(logging.TRACE, msg, *args, **kwargs)
