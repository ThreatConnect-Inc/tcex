"""Internal Threading Logic"""
# standard library
import logging
import threading

# first-party
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module

logger: TraceLogger = logging.getLogger('tcex')  # type: ignore


class ExceptionThread(threading.Thread):
    """Thread that saves any uncaught exception into an instance variable for further inspection"""

    def __init__(self, *args, **kwargs):
        """Initialize thread"""
        super().__init__(*args, **kwargs)
        self.exception = None

    def run(self):
        """Run thread logic"""
        try:
            super().run()
        except Exception as ex:
            self.exception = ex
            logger.exception(f'Unexpected exception occurred in thread with name: {self.name}')
            # let exception logic continue as normal
            raise ex
