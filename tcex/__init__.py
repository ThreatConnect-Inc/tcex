"""TcEx Framework module init file."""
# flake8: noqa
# standard library
import logging

# first-party
from tcex.logger.cache_handler import CacheHandler  # pylint: disable=no-name-in-module
from tcex.logger.trace_logger import TraceLogger  # pylint: disable=no-name-in-module

# init logger before instantiating tcex
logging.setLoggerClass(TraceLogger)
logger = logging.getLogger('tcex')
logger.setLevel(logging.TRACE)  # pylint: disable=E1101

# add TEMP cache handler, which will be removed in tcex.py (we don't know log path here)
cache = CacheHandler()
cache.set_name('cache')
cache.setLevel(logging.TRACE)  # pylint: disable=no-member
cache.setFormatter(
    '%(asctime)s - %(name)s - %(levelname)8s - %(message)s '
    '(%(filename)s:%(funcName)s:%(lineno)d)'
)
logger.addHandler(cache)

# pylint: disable=wrong-import-position
from .__metadata__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __package_name__,
    __url__,
    __version__,
)

try:
    # first-party
    from tcex.tcex import TcEx
except ImportError as e:
    print(f'Error: {e}')
    print('Try running tclib')
    raise
