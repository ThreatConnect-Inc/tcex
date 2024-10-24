"""TcEx Framework Module"""

# standard library
import logging
from inspect import getframeinfo, stack

# Create trace logging level
logging.TRACE = logging.DEBUG - 5  # type: ignore
logging.addLevelName(logging.TRACE, 'TRACE')  # type: ignore


class TraceLogger(logging.Logger):
    """Add trace level to logging"""

    # supports updated call for Python 3.8
    def findCaller(
        self, stack_info=False, stacklevel=1
    ) -> tuple:  # pylint: disable=arguments-differ,unused-argument
        """Find the caller for the current log event."""
        caller = None
        depth = 3
        while True:
            # search for the correct calling method
            caller = getframeinfo(stack()[depth][0])
            if caller.function != 'trace' or depth >= 6:
                break
            depth += 1

        return (caller.filename, caller.lineno, caller.function, None)

    def trace(self, msg, *args, **kwargs):
        """Set trace logging level."""
        self.log(logging.TRACE, msg, *args, **kwargs)  # type: ignore
