"""TcEx Framework Module"""

# ruff: noqa: F401

# standard library
import logging

# first-party
from tcex.__metadata__ import __license__, __version__
from tcex.logger.cache_handler import CacheHandler
from tcex.logger.trace_logger import TraceLogger


def initialize_logger():
    """Initialize logger TraceLogger."""
    # init logger before instantiating tcex
    logging.setLoggerClass(TraceLogger)
    _logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore
    _logger.setLevel(logging.TRACE)  # type: ignore

    # add TEMP cache handler, which will be removed in tcex.py (we don't know log path here)
    cache = CacheHandler()
    cache.set_name('cache')
    cache.setLevel(logging.TRACE)  # type: ignore
    cache.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)8s - %(message)s '
            '(%(filename)s:%(funcName)s:%(lineno)d)'
        )
    )
    _logger.addHandler(cache)


# init logger before instantiating tcex
initialize_logger()

try:
    # first-party
    from tcex.tcex import TcEx  # noqa: F401
except ImportError as ex:
    print(f'Error: {ex}')
    print('Try running tcex deps')
